#!/usr/bin/env python3
"""Contract tests for the source-specific arXiv query repair."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "repair_arxiv_queries_v4.py"


def load_module():
    spec = importlib.util.spec_from_file_location("repair_arxiv_queries_v4", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load arXiv query repair module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArxivQueryContractTests(unittest.TestCase):
    def test_six_claim_bound_queries_are_explicitly_scoped(self) -> None:
        module = load_module()
        queries = module.ARXIV_QUERIES
        self.assertEqual(set(queries), {f"Q{index:03d}" for index in range(1, 7)})
        for query in queries.values():
            self.assertIn('all:"central bank digital currenc', query.lower())
            self.assertIn(" AND ", query)
            self.assertNotRegex(query, r"^all:[^\"]*central bank digital currency")

    def test_query_validation_rejects_the_legacy_broad_form(self) -> None:
        module = load_module()
        legacy = "all:central bank digital currency composable assurance privacy"
        with self.assertRaises(ValueError):
            module.validate_arxiv_query(legacy)

    def test_query_validation_accepts_every_repaired_query(self) -> None:
        module = load_module()
        for query in module.ARXIV_QUERIES.values():
            module.validate_arxiv_query(query)


if __name__ == "__main__":
    unittest.main()
