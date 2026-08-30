import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_primary_search_v4.py")


def load_module():
    spec = importlib.util.spec_from_file_location("verify_primary_search_v4", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PrimarySearchVerifierTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_current_full_text_and_citation_chain_contract(self):
        result = self.module.verify_citation_chain_evidence(MODULE_PATH.parent)
        self.assertEqual(result["citation_chain_rows"], 79)
        self.assertEqual(result["cev_feature_rows"], 11)
        self.assertEqual(result["retained_cev_forward_citations"], 11)
        self.assertEqual(result["novelty_verdict"], "UNRESOLVED")
        self.assertFalse(result["scientific_verification_performed"])

    def test_hash_manifest_rejects_tampered_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            captured = root / "captured.json"
            captured.write_text(json.dumps({"captured": True}), encoding="utf-8")
            summary = {
                "input_manifest": [
                    {
                        "path": "captured.json",
                        "bytes": captured.stat().st_size,
                        "sha256": "0" * 64,
                    }
                ]
            }
            with self.assertRaises(AssertionError):
                self.module.verify_input_manifest(summary, root)


if __name__ == "__main__":
    unittest.main()
