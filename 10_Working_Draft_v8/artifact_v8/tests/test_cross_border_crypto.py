from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from cross_border_bft_v5 import canon, digest, sign, verify


def test_canonical_serialization_is_order_independent() -> None:
    left = {"b": [2, 1], "a": {"y": 2, "x": 1}}
    right = {"a": {"x": 1, "y": 2}, "b": [2, 1]}
    assert canon(left) == canon(right)
    assert digest(left) == digest(right)


def test_signature_rejects_tampering() -> None:
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    evidence = {"tx": "T-001", "amount": 100, "currency": "CUR-A"}
    signature = sign(private, evidence)
    assert verify(public, evidence, signature)
    assert not verify(public, {**evidence, "amount": 101}, signature)


def test_signature_rejects_malformed_encoding() -> None:
    private = Ed25519PrivateKey.generate()
    assert not verify(private.public_key(), {"tx": "T-001"}, "not-base64!")
