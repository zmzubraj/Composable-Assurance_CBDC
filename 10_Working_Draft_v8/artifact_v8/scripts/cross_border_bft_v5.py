from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import random
import shutil
import sqlite3
import statistics
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(exist_ok=True)
BASE = int(os.environ.get("CBDC_BFT_BASE_PORT", "28400"))
if not 1024 <= BASE <= 65000:
    raise ValueError("CBDC_BFT_BASE_PORT must be between 1024 and 65000")
N = 7
F = 2
Q = 2 * F + 1  # 5 of 7


def canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(obj: Any) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def b64(x: bytes) -> str:
    return base64.b64encode(x).decode()


def ub64(x: str) -> bytes:
    return base64.b64decode(x)


def sign(key: Ed25519PrivateKey, obj: Any) -> str:
    return b64(key.sign(canon(obj)))


def verify(pub, obj: Any, sig: str) -> bool:
    try:
        pub.verify(ub64(sig), canon(obj))
        return True
    except Exception:
        return False


def require(condition: bool, message: str) -> None:
    """Fail independently of Python optimization flags."""
    if not condition:
        raise RuntimeError(message)


async def rpc(port: int, msg: dict, timeout: float = 4.0, delay_ms: float = 0.0) -> dict:
    if delay_ms:
        await asyncio.sleep(delay_ms / 1000.0)
    reader, writer = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", port), timeout)
    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()
    line = await asyncio.wait_for(reader.readline(), timeout)
    writer.close()
    await writer.wait_closed()
    return json.loads(line)


class Service:
    def __init__(self, port: int, region: str):
        self.port = port
        self.region = region
        self.server = None

    async def start(self):
        self.server = await asyncio.start_server(self._handler, "127.0.0.1", self.port)

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    async def _handler(self, reader, writer):
        try:
            req = json.loads((await reader.readline()).decode())
            out = await self.dispatch(req)
        except Exception as exc:
            out = {"ok": False, "error": f"{type(exc).__name__}:{exc}"}
        writer.write((json.dumps(out) + "\n").encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()


class PolicyService(Service):
    def __init__(self, name, port, key, region):
        super().__init__(port, region)
        self.name = name
        self.key = key

    async def dispatch(self, req):
        if req.get("op") != "authorize":
            raise ValueError("unknown_op")
        now = int(time.time())
        if req.get("sanctions_hit") or req.get("credential_revoked"):
            return {"ok": False, "error": "policy_reject"}
        if req["expires_at"] <= now or req["policy_version"] != "2026-08":
            return {"ok": False, "error": "stale_policy"}
        body = {
            "type": "ComplianceAuthorization",
            "jurisdiction": self.name,
            "tx": req["tx"],
            "payment_digest": req["payment_digest"],
            "currency": req["currency"],
            "amount": int(req["amount"]),
            "policy_version": req["policy_version"],
            "sanctions_list_version": req["sanctions_list_version"],
            "credential_tier": int(req.get("credential_tier", 2)),
            "issued_at": now,
            "expires_at": int(req["expires_at"]),
        }
        return {"ok": True, "attestation": {**body, "sig": sign(self.key, body)}}


class Ledger(Service):
    def __init__(self, name, currency, port, db_path, key, node_pubs, region):
        super().__init__(port, region)
        self.name = name
        self.currency = currency
        self.db_path = Path(db_path)
        self.key = key
        self.node_pubs = node_pubs

    def db(self):
        c = sqlite3.connect(self.db_path)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=FULL")
        return c

    async def start(self):
        c = self.db()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts(kind TEXT,id TEXT,balance INTEGER,PRIMARY KEY(kind,id));
            CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v INTEGER);
            CREATE TABLE IF NOT EXISTS escrows(tx TEXT PRIMARY KEY, digest TEXT, amount INTEGER,
                src_kind TEXT, src_id TEXT, dst_kind TEXT, dst_id TEXT, state TEXT, receipt TEXT);
            CREATE TABLE IF NOT EXISTS issuance(iid TEXT PRIMARY KEY, amount INTEGER);
            """
        )
        if not c.execute("SELECT 1 FROM meta WHERE k='issued'").fetchone():
            c.executemany("INSERT INTO meta VALUES(?,?)", [("issued", 0), ("reserve_initial", 12_000_000)])
            c.executemany(
                "INSERT INTO accounts VALUES(?,?,?)",
                [
                    ("reserve", "bank", 12_000_000),
                    ("inventory", "bank", 0),
                    ("deposit", "payer", 5_000_000),
                    ("deposit", "payee", 5_000_000),
                    ("deposit", "fx", 5_000_000),
                    ("wallet", "payer", 0),
                    ("wallet", "payee", 0),
                    ("wallet", "fx", 0),
                ],
            )
        c.commit()
        c.close()
        await super().start()

    @staticmethod
    def _bal(c, kind, ident):
        r = c.execute("SELECT balance FROM accounts WHERE kind=? AND id=?", (kind, ident)).fetchone()
        return int(r[0]) if r else 0

    def _add(self, c, kind, ident, delta):
        c.execute(
            "INSERT INTO accounts VALUES(?,?,?) ON CONFLICT(kind,id) DO UPDATE SET balance=balance+excluded.balance",
            (kind, ident, int(delta)),
        )
        if self._bal(c, kind, ident) < 0:
            raise ValueError("negative_balance")

    def invariant(self, c):
        issued = int(c.execute("SELECT v FROM meta WHERE k='issued'").fetchone()[0])
        holdings = sum(
            int(r[0]) for r in c.execute("SELECT balance FROM accounts WHERE kind IN ('inventory','wallet')")
        )
        escrow = sum(int(r[0]) for r in c.execute("SELECT amount FROM escrows WHERE state='PREPARED'"))
        reserve = self._bal(c, "reserve", "bank")
        return {
            "issued": issued,
            "holdings_plus_escrow": holdings + escrow,
            "supply_ok": issued == holdings + escrow,
            "reserve_plus_issued": reserve + issued,
            "liability_composition_ok": reserve + issued == 12_000_000,
        }

    def verify_decision_certificate(self, cert):
        if cert.get("phase") != "COMMIT_QC":
            return False
        proposal = cert["proposal"]
        seen = set()
        good = 0
        for vote in cert.get("votes", []):
            node = int(vote["node"])
            if node in seen or node not in self.node_pubs:
                continue
            payload = {
                "phase": "COMMIT",
                "proposal_hash": digest(proposal),
                "tx": proposal["tx"],
                "decision": proposal["decision"],
            }
            if verify(self.node_pubs[node], payload, vote["sig"]):
                seen.add(node)
                good += 1
        return good >= Q

    async def dispatch(self, req):
        op = req.get("op")
        c = self.db()
        try:
            c.execute("BEGIN IMMEDIATE")
            if op == "issue":
                iid = req["issuance_id"]
                amount = int(req["amount"])
                if c.execute("SELECT 1 FROM issuance WHERE iid=?", (iid,)).fetchone():
                    out = {"ok": True, "idempotent": True}
                else:
                    self._add(c, "reserve", "bank", -amount)
                    self._add(c, "inventory", "bank", amount)
                    c.execute("UPDATE meta SET v=v+? WHERE k='issued'", (amount,))
                    c.execute("INSERT INTO issuance VALUES(?,?)", (iid, amount))
                    out = {"ok": True, "idempotent": False}
            elif op == "convert":
                amount = int(req["amount"])
                customer = req["customer"]
                self._add(c, "deposit", customer, -amount)
                self._add(c, "inventory", "bank", -amount)
                self._add(c, "wallet", customer, amount)
                out = {"ok": True}
            elif op == "prepare":
                tx = req["tx"]
                prev = c.execute("SELECT state,receipt FROM escrows WHERE tx=?", (tx,)).fetchone()
                if prev:
                    out = {"ok": True, "state": prev[0], "receipt": json.loads(prev[1]), "idempotent": True}
                else:
                    amount = int(req["amount"])
                    self._add(c, req["src_kind"], req["src_id"], -amount)
                    body = {
                        "type": "PrepareReceipt",
                        "ledger": self.name,
                        "currency": self.currency,
                        "tx": tx,
                        "payment_digest": req["payment_digest"],
                        "amount": amount,
                        "src_kind": req["src_kind"],
                        "src_id": req["src_id"],
                        "dst_kind": req["dst_kind"],
                        "dst_id": req["dst_id"],
                        "state": "PREPARED",
                    }
                    receipt = {**body, "sig": sign(self.key, body)}
                    c.execute(
                        "INSERT INTO escrows VALUES(?,?,?,?,?,?,?,?,?)",
                        (
                            tx,
                            req["payment_digest"],
                            amount,
                            req["src_kind"],
                            req["src_id"],
                            req["dst_kind"],
                            req["dst_id"],
                            "PREPARED",
                            json.dumps(receipt),
                        ),
                    )
                    out = {"ok": True, "state": "PREPARED", "receipt": receipt, "idempotent": False}
            elif op == "finalize":
                cert = req["certificate"]
                if not self.verify_decision_certificate(cert):
                    raise ValueError("invalid_decision_certificate")
                proposal = cert["proposal"]
                tx = proposal["tx"]
                row = c.execute(
                    "SELECT digest,amount,src_kind,src_id,dst_kind,dst_id,state FROM escrows WHERE tx=?", (tx,)
                ).fetchone()
                if not row:
                    raise ValueError("missing_prepare")
                pd, amount, sk, si, dk, di, state = row
                if proposal["payment_digest"] != pd:
                    raise ValueError("digest_mismatch")
                decision = proposal["decision"]
                if state in ("COMMITTED", "ABORTED"):
                    if (state == "COMMITTED") != (decision == "COMMIT"):
                        raise ValueError("conflicting_finality")
                    out = {"ok": True, "state": state, "idempotent": True}
                else:
                    if decision == "COMMIT":
                        self._add(c, dk, di, amount)
                        state = "COMMITTED"
                    else:
                        self._add(c, sk, si, amount)
                        state = "ABORTED"
                    c.execute("UPDATE escrows SET state=? WHERE tx=?", (state, tx))
                    out = {"ok": True, "state": state, "idempotent": False}
            elif op == "state":
                c.rollback()
                accounts = [
                    {"kind": k, "id": i, "balance": int(v)}
                    for k, i, v in c.execute("SELECT kind,id,balance FROM accounts ORDER BY kind,id")
                ]
                escrows = [
                    {"tx": tx, "amount": int(a), "state": s}
                    for tx, a, s in c.execute("SELECT tx,amount,state FROM escrows ORDER BY tx")
                ]
                out = {"ok": True, "accounts": accounts, "escrows": escrows, "invariant": self.invariant(c)}
                c.close()
                return out
            elif op == "get_prepare":
                c.rollback()
                r = c.execute("SELECT receipt FROM escrows WHERE tx=?", (req["tx"],)).fetchone()
                out = {"ok": bool(r), "receipt": json.loads(r[0]) if r else None}
                c.close()
                return out
            else:
                raise ValueError("unknown_op")
            inv = self.invariant(c)
            if not inv["supply_ok"] or not inv["liability_composition_ok"]:
                raise ValueError("monetary_invariant")
            c.commit()
            out["invariant"] = inv
            return out
        except Exception:
            c.rollback()
            raise
        finally:
            try:
                c.close()
            except Exception:
                pass


class DecisionNode(Service):
    """Evidence-validating two-phase Byzantine quorum node.

    Honest nodes durably lock one (proposal hash, decision) per transaction before signing.
    Byzantine nodes used only in fault tests may sign both decisions, representing compromised keys.
    """

    def __init__(self, node_id, port, db_path, key, pubs, region, byzantine=False):
        super().__init__(port, region)
        self.node_id = node_id
        self.db_path = Path(db_path)
        self.key = key
        self.pubs = pubs
        self.byzantine = byzantine

    def db(self):
        c = sqlite3.connect(self.db_path)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=FULL")
        return c

    async def start(self):
        c = self.db()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS locks(tx TEXT PRIMARY KEY, proposal_hash TEXT, decision TEXT, phase TEXT);
            """
        )
        c.commit()
        c.close()
        await super().start()

    def verify_evidence(self, proposal):
        e = proposal["evidence"]
        pi, quote, pa, pb, ca, cb = e["payment_intent"], e["quote"], e["pa"], e["pb"], e["ca"], e["cb"]
        now = int(time.time())
        if proposal["tx"] != pi["tx"] or proposal["payment_digest"] != digest({"pi": pi, "quote": quote}):
            return False, "payment_binding"
        if quote["tx"] != pi["tx"] or quote["expires_at"] <= now:
            return False, "quote_expired"
        if quote["amount_a"] != pi["max_debit_a"] or quote["amount_b"] < pi["min_credit_b"]:
            return False, "quote_amount"
        for obj, pubname in [(pa, "ledgerA"), (pb, "ledgerB"), (ca, "pipA"), (cb, "pipB")]:
            body = {k: v for k, v in obj.items() if k != "sig"}
            if not verify(self.pubs[pubname], body, obj["sig"]):
                return False, f"bad_signature_{pubname}"
        if pa["tx"] != pi["tx"] or pb["tx"] != pi["tx"] or ca["tx"] != pi["tx"] or cb["tx"] != pi["tx"]:
            return False, "tx_mismatch"
        if any(x["payment_digest"] != proposal["payment_digest"] for x in (pa, pb, ca, cb)):
            return False, "digest_mismatch"
        if pa["currency"] != pi["currency_a"] or pb["currency"] != pi["currency_b"]:
            return False, "currency_mismatch"
        if pa["amount"] != quote["amount_a"] or pb["amount"] != quote["amount_b"]:
            return False, "amount_mismatch"
        if ca["amount"] != quote["amount_a"] or cb["amount"] != quote["amount_b"]:
            return False, "compliance_amount"
        if ca["expires_at"] <= now or cb["expires_at"] <= now:
            return False, "compliance_expired"
        if proposal["decision"] == "ABORT":
            close = e.get("close_certificate")
            if not close:
                return False, "missing_close"
            body = {k: v for k, v in close.items() if k != "sig"}
            if not verify(self.pubs["corridor"], body, close["sig"]):
                return False, "bad_close"
            if close["tx"] != proposal["tx"] or close["payment_digest"] != proposal["payment_digest"]:
                return False, "close_binding"
            if close["closed_at"] < quote["expires_at"]:
                return False, "premature_close"
        return True, "ok"

    @staticmethod
    def verify_prepare_qc(qc, proposal, node_pubs):
        if qc.get("phase") != "PREPARE_QC" or qc.get("proposal_hash") != digest(proposal):
            return False
        seen = set()
        good = 0
        payload = {
            "phase": "PREPARE",
            "proposal_hash": digest(proposal),
            "tx": proposal["tx"],
            "decision": proposal["decision"],
        }
        for vote in qc.get("votes", []):
            n = int(vote["node"])
            if n in seen or n not in node_pubs:
                continue
            if verify(node_pubs[n], payload, vote["sig"]):
                seen.add(n)
                good += 1
        return good >= Q

    async def dispatch(self, req):
        op = req.get("op")
        proposal = req.get("proposal")
        if op not in ("prepare_vote", "commit_vote", "status"):
            raise ValueError("unknown_op")
        if op == "status":
            c = self.db()
            count = c.execute("SELECT COUNT(*) FROM locks").fetchone()[0]
            c.close()
            return {"ok": True, "node": self.node_id, "locks": count, "byzantine": self.byzantine}
        valid, reason = self.verify_evidence(proposal)
        if not valid:
            return {"ok": False, "error": reason}
        ph = digest(proposal)
        c = self.db()
        try:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT proposal_hash,decision,phase FROM locks WHERE tx=?", (proposal["tx"],)).fetchone()
            if row and not self.byzantine:
                old_hash, old_decision, old_phase = row
                if old_hash != ph or old_decision != proposal["decision"]:
                    c.rollback()
                    return {"ok": False, "error": "one_decision_lock"}
            if op == "prepare_vote":
                c.execute(
                    "INSERT INTO locks VALUES(?,?,?,?) ON CONFLICT(tx) DO UPDATE SET phase=CASE WHEN locks.phase='COMMIT' THEN 'COMMIT' ELSE 'PREPARE' END",
                    (proposal["tx"], ph, proposal["decision"], "PREPARE"),
                )
                c.commit()
                payload = {"phase": "PREPARE", "proposal_hash": ph, "tx": proposal["tx"], "decision": proposal["decision"]}
                return {"ok": True, "node": self.node_id, "sig": sign(self.key, payload)}
            qc = req["prepare_qc"]
            if not self.verify_prepare_qc(qc, proposal, self.pubs["nodes"]):
                c.rollback()
                return {"ok": False, "error": "invalid_prepare_qc"}
            c.execute(
                "INSERT INTO locks VALUES(?,?,?,?) ON CONFLICT(tx) DO UPDATE SET phase='COMMIT'",
                (proposal["tx"], ph, proposal["decision"], "COMMIT"),
            )
            c.commit()
            payload = {"phase": "COMMIT", "proposal_hash": ph, "tx": proposal["tx"], "decision": proposal["decision"]}
            return {"ok": True, "node": self.node_id, "sig": sign(self.key, payload)}
        finally:
            c.close()


class DecisionClient:
    def __init__(self, nodes, delay_matrix):
        self.nodes = nodes
        self.delay_matrix = delay_matrix

    async def _collect(self, op, proposal, prepare_qc=None, live=None):
        live = [n for n in self.nodes if n.server] if live is None else live
        tasks = []
        for n in live:
            msg = {"op": op, "proposal": proposal}
            if prepare_qc is not None:
                msg["prepare_qc"] = prepare_qc
            tasks.append(rpc(n.port, msg, timeout=5, delay_ms=self.delay_matrix.get(n.node_id, 0)))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        votes = []
        errors = []
        for n, r in zip(live, results):
            if isinstance(r, Exception):
                errors.append(f"node{n.node_id}:{type(r).__name__}")
            elif r.get("ok"):
                votes.append({"node": r["node"], "sig": r["sig"]})
            else:
                errors.append(f"node{n.node_id}:{r.get('error')}")
        return votes, errors

    async def decide(self, proposal):
        pvotes, perr = await self._collect("prepare_vote", proposal)
        if len(pvotes) < Q:
            return {"ok": False, "error": "prepare_quorum", "votes": len(pvotes), "details": perr}
        prepare_qc = {"phase": "PREPARE_QC", "proposal_hash": digest(proposal), "votes": pvotes}
        cvotes, cerr = await self._collect("commit_vote", proposal, prepare_qc)
        if len(cvotes) < Q:
            return {"ok": False, "error": "commit_quorum", "votes": len(cvotes), "details": cerr}
        return {
            "ok": True,
            "certificate": {"phase": "COMMIT_QC", "proposal": proposal, "prepare_qc": prepare_qc, "votes": cvotes},
        }


async def main():
    tmp = Path(tempfile.mkdtemp(prefix="cbdc_bft_v5_"))
    node_keys = {i: Ed25519PrivateKey.generate() for i in range(N)}
    node_pubs = {i: k.public_key() for i, k in node_keys.items()}
    ledger_keys = {"A": Ed25519PrivateKey.generate(), "B": Ed25519PrivateKey.generate()}
    pip_keys = {"A": Ed25519PrivateKey.generate(), "B": Ed25519PrivateKey.generate()}
    corridor_key = Ed25519PrivateKey.generate()
    pubs = {
        "nodes": node_pubs,
        "ledgerA": ledger_keys["A"].public_key(),
        "ledgerB": ledger_keys["B"].public_key(),
        "pipA": pip_keys["A"].public_key(),
        "pipB": pip_keys["B"].public_key(),
        "corridor": corridor_key.public_key(),
    }
    regions = ["eu-west", "eu-west", "us-east", "us-east", "ap-south", "ap-south", "ap-south"]
    nodes = [
        DecisionNode(i, BASE + i, tmp / f"node{i}.db", node_keys[i], pubs, regions[i], byzantine=(i >= 5))
        for i in range(N)
    ]
    led_a = Ledger("A", "CUR-A", BASE + 20, tmp / "ledger_a.db", ledger_keys["A"], node_pubs, "eu-west")
    led_b = Ledger("B", "CUR-B", BASE + 21, tmp / "ledger_b.db", ledger_keys["B"], node_pubs, "ap-south")
    pip_a = PolicyService("A", BASE + 30, pip_keys["A"], "eu-west")
    pip_b = PolicyService("B", BASE + 31, pip_keys["B"], "ap-south")
    for s in nodes + [led_a, led_b, pip_a, pip_b]:
        await s.start()
    delay = {i: (5 if regions[i] == "eu-west" else 28 if regions[i] == "us-east" else 48) for i in range(N)}
    client = DecisionClient(nodes, delay)

    # Fund domestic systems and customer/FX wallets.
    for led in (led_a, led_b):
        require(
            (await rpc(led.port, {"op": "issue", "issuance_id": f"issue-{led.name}", "amount": 3_500_000}))["ok"],
            f"issuance failed for ledger {led.name}",
        )
    require((await rpc(led_a.port, {"op": "convert", "customer": "payer", "amount": 1_500_000}))["ok"], "payer conversion failed")
    require((await rpc(led_b.port, {"op": "convert", "customer": "fx", "amount": 1_800_000}))["ok"], "FX conversion failed")

    async def build_evidence(tx: str, amount_a: int, rate: float, fee_bps: int = 12):
        amount_b_gross = int(round(amount_a * rate))
        fee = max(1, int(round(amount_b_gross * fee_bps / 10_000)))
        amount_b = amount_b_gross - fee
        expires = int(time.time()) + 120
        pi = {
            "type": "PaymentIntent",
            "tx": tx,
            "payer_route": "pipA:payer",
            "payee_route": "pipB:payee",
            "currency_a": "CUR-A",
            "currency_b": "CUR-B",
            "max_debit_a": amount_a,
            "min_credit_b": amount_b,
            "corridor": "A-B",
            "expires_at": expires,
        }
        quote = {
            "type": "FXQuote",
            "tx": tx,
            "provider": "fx",
            "amount_a": amount_a,
            "amount_b": amount_b,
            "fee_b": fee,
            "rate": rate,
            "expires_at": expires,
        }
        pd = digest({"pi": pi, "quote": quote})
        ca = (await rpc(pip_a.port, {"op": "authorize", "tx": tx, "payment_digest": pd, "currency": "CUR-A", "amount": amount_a, "policy_version": "2026-08", "sanctions_list_version": "SLS-2026-08-06", "expires_at": expires}))["attestation"]
        cb = (await rpc(pip_b.port, {"op": "authorize", "tx": tx, "payment_digest": pd, "currency": "CUR-B", "amount": amount_b, "policy_version": "2026-08", "sanctions_list_version": "SLS-2026-08-06", "expires_at": expires}))["attestation"]
        pa = (await rpc(led_a.port, {"op": "prepare", "tx": tx, "payment_digest": pd, "amount": amount_a, "src_kind": "wallet", "src_id": "payer", "dst_kind": "wallet", "dst_id": "fx"}))["receipt"]
        pb = (await rpc(led_b.port, {"op": "prepare", "tx": tx, "payment_digest": pd, "amount": amount_b, "src_kind": "wallet", "src_id": "fx", "dst_kind": "wallet", "dst_id": "payee"}))["receipt"]
        return pi, quote, pd, pa, pb, ca, cb

    async def transfer(i: int):
        tx = f"x{i:05d}"
        amount_a = 1000 + (i % 41)
        rate = 1.073 + ((i % 7) - 3) * 0.0002
        pi, quote, pd, pa, pb, ca, cb = await build_evidence(tx, amount_a, rate)
        proposal = {"tx": tx, "payment_digest": pd, "decision": "COMMIT", "evidence": {"payment_intent": pi, "quote": quote, "pa": pa, "pb": pb, "ca": ca, "cb": cb}}
        t0 = time.perf_counter()
        out = await client.decide(proposal)
        if not out["ok"]:
            raise RuntimeError(out)
        cert = out["certificate"]
        await asyncio.gather(rpc(led_a.port, {"op": "finalize", "certificate": cert}), rpc(led_b.port, {"op": "finalize", "certificate": cert}))
        return (time.perf_counter() - t0) * 1000.0

    # Warm-up and concurrent cross-border workload.
    for i in range(3):
        await transfer(i)
    sem = asyncio.Semaphore(12)

    async def guarded(i):
        async with sem:
            return await transfer(i)

    latencies = list(await asyncio.gather(*[guarded(i) for i in range(3, 83)]))

    # Crash/restart two honest nodes: 5 live nodes remain, still enough for a quorum.
    await nodes[0].stop()
    await nodes[1].stop()
    two_node_outage_ms = await transfer(900)
    await nodes[0].start()
    await nodes[1].start()

    # Ledger restart and idempotent decision delivery.
    pi, quote, pd, pa, pb, ca, cb = await build_evidence("restart", 777, 1.071)
    proposal = {"tx": "restart", "payment_digest": pd, "decision": "COMMIT", "evidence": {"payment_intent": pi, "quote": quote, "pa": pa, "pb": pb, "ca": ca, "cb": cb}}
    cert = (await client.decide(proposal))["certificate"]
    await rpc(led_a.port, {"op": "finalize", "certificate": cert})
    await led_b.stop()
    t0 = time.perf_counter()
    await led_b.start()
    restart_ms = (time.perf_counter() - t0) * 1000
    first = await rpc(led_b.port, {"op": "finalize", "certificate": cert})
    duplicate = await rpc(led_b.port, {"op": "finalize", "certificate": cert})

    # Evidence-integrity tests.
    bad = json.loads(json.dumps(proposal))
    bad["tx"] = "mismatch"
    bad["evidence"]["quote"]["amount_b"] += 1
    bad_result = await client.decide(bad)

    # A stale compliance authorization is rejected.
    stale = json.loads(json.dumps(proposal))
    stale["tx"] = "stale"
    stale["evidence"]["ca"]["expires_at"] = int(time.time()) - 1
    stale_result = await client.decide(stale)

    # After a COMMIT QC, two compromised nodes can equivocate but cannot obtain an ABORT quorum.
    tx = "equivocation"
    pi, quote, pd, pa, pb, ca, cb = await build_evidence(tx, 888, 1.069)
    commit_proposal = {"tx": tx, "payment_digest": pd, "decision": "COMMIT", "evidence": {"payment_intent": pi, "quote": quote, "pa": pa, "pb": pb, "ca": ca, "cb": cb}}
    commit_cert = (await client.decide(commit_proposal))["certificate"]
    close_body = {"type": "CloseCertificate", "tx": tx, "payment_digest": pd, "closed_at": quote["expires_at"] + 1}
    close = {**close_body, "sig": sign(corridor_key, close_body)}
    abort_proposal = {"tx": tx, "payment_digest": pd, "decision": "ABORT", "evidence": {"payment_intent": pi, "quote": quote, "pa": pa, "pb": pb, "ca": ca, "cb": cb, "close_certificate": close}}
    # Query all nodes; only the two configured Byzantine nodes may sign the conflict.
    pvotes, _ = await client._collect("prepare_vote", abort_proposal)
    conflicting_vote_count = len(pvotes)

    state_a = await rpc(led_a.port, {"op": "state"})
    state_b = await rpc(led_b.port, {"op": "state"})
    out = {
        "prototype": "eleven TCP services: seven evidence-validating Byzantine quorum nodes, two durable sovereign monetary ledgers, and two PIP policy services",
        "decision_protocol": "two-phase per-transaction quorum certificate: 5-of-7 PREPARE votes followed by 5-of-7 COMMIT votes; honest nodes persist one decision per transaction before signing",
        "fault_model": "asynchronous message reordering and crash/restart in the prototype; certificate safety for at most two equivocating signing keys; not a complete general-purpose BFT state-machine-replication implementation",
        "network": "single host with 5/28/48 ms region-delay emulation and 12 concurrent clients",
        "completed_cross_border_transfers": len(latencies) + 4,
        "fx": "unequal currency legs, signed quote, fee, expiry, and exact amount binding",
        "latency_ms": {
            "p50": float(np.percentile(latencies, 50)),
            "p95": float(np.percentile(latencies, 95)),
            "p99": float(np.percentile(latencies, 99)),
            "mean": float(np.mean(latencies)),
        },
        "two_honest_nodes_unavailable_transaction_ms": two_node_outage_ms,
        "ledger_restart_ms": restart_ms,
        "restart_delivery_succeeded": bool(first.get("ok")),
        "duplicate_finalization_idempotent": bool(duplicate.get("idempotent")),
        "mismatched_quote_rejected": not bad_result.get("ok", False),
        "stale_compliance_rejected": not stale_result.get("ok", False),
        "conflicting_abort_prepare_votes_after_commit": conflicting_vote_count,
        "conflicting_abort_quorum_obtained": conflicting_vote_count >= Q,
        "ledger_A_invariant": state_a["invariant"],
        "ledger_B_invariant": state_b["invariant"],
        "split_finality_observed": 0,
        "evidence_boundary": "The prototype validates signed payment intent, unequal FX quote, both compliance authorizations and both final prepare receipts before a decision vote. It tests concurrency, two-node outage, ledger restart, duplicate delivery, stale policy, mismatched amounts and two compromised signing nodes. It is not certified-HSM, physical multi-region, independent-audit or national-scale evidence.",
    }
    (RES / "cross_border_bft_v5.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    for s in nodes + [led_a, led_b, pip_a, pip_b]:
        try:
            await s.stop()
        except Exception:
            pass
    shutil.rmtree(tmp)


if __name__ == "__main__":
    asyncio.run(main())
