#!/usr/bin/env python3
"""Contract tests for the fail-closed title/abstract screening ledger."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "build_screening_ledger_v4.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_screening_ledger_v4", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load screening module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScreeningContractTests(unittest.TestCase):
    def test_non_cbdc_record_is_excluded_as_out_of_scope(self) -> None:
        module = load_module()
        decision = module.classify_record("Atomic traps for neutral atoms", "A physics experiment.")
        self.assertEqual(decision[0], "EXCLUDE_OUT_OF_SCOPE")

    def test_cross_border_cbdc_protocol_is_prioritized(self) -> None:
        module = load_module()
        decision = module.classify_record(
            "Cross-border CBDC settlement with compliance certificates",
            "The protocol coordinates independent ledgers with atomic finality and AML evidence.",
        )
        self.assertEqual(decision[0], "PRIORITY_FULL_TEXT")
        self.assertIn("settlement", decision[1])
        self.assertIn("financial_integrity", decision[1])

    def test_generic_monetary_policy_record_is_excluded(self) -> None:
        module = load_module()
        decision = module.classify_record(
            "Central Bank Digital Currency and Monetary Policy",
            "We estimate household demand and the effects on bank profitability.",
        )
        self.assertEqual(decision[0], "EXCLUDE_GENERIC_CBDC")

    def test_missing_abstract_cannot_support_a_final_exclusion(self) -> None:
        module = load_module()
        decision = module.classify_record("Central Bank Digital Currency", "")
        self.assertEqual(decision[0], "RETRIEVE_ABSTRACT_OR_FULL_TEXT")

    def test_cbdc_evaluation_and_verification_framework_is_prioritized(self) -> None:
        module = load_module()
        decision = module.classify_record(
            "CEV Framework: A Central Bank Digital Currency Evaluation and Verification Framework",
            "The framework recommends technical solutions and verifies them using empirical experiments and formal proof.",
        )
        self.assertEqual(decision[0], "PRIORITY_FULL_TEXT")


if __name__ == "__main__":
    unittest.main()
