import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_citation_chains_v4.py")


def load_module():
    spec = importlib.util.spec_from_file_location("build_citation_chains_v4", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CitationChainBuilderTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_forward_screen_rejects_unrelated_openalex_noise(self):
        decision, impact = self.module.classify_title(
            "Optimization of industrial waste composition for eco-cement production",
            "forward",
        )
        self.assertEqual(decision, "EXCLUDE_NON_CBDC_CITATION")
        self.assertEqual(impact, "NO_C001_IMPACT")

    def test_forward_screen_retains_cbdc_citation(self):
        decision, impact = self.module.classify_title(
            "A systematic review of central bank digital currency architectures",
            "forward",
        )
        self.assertEqual(decision, "RETAIN_CBDC_CITATION")
        self.assertEqual(impact, "CHECKS_LATER_INTERPRETATION_OF_CEV")

    def test_crossref_reference_title_falls_back_to_journal_title(self):
        ref = {"key": "ref1", "year": "2022", "journal-title": "Project mBridge: Connecting economies through CBDC interoperability"}
        row = self.module.normalize_crossref_reference(ref, "SSRN539", "backward")
        self.assertEqual(row["title"], "Project mBridge: Connecting economies through CBDC interoperability")
        self.assertEqual(row["year"], "2022")

    def test_manifest_hashes_every_captured_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            source.write_text(json.dumps({"ok": True}), encoding="utf-8")
            manifest = self.module.hash_manifest([source], root)
            self.assertEqual(manifest[0]["path"], "source.json")
            self.assertEqual(len(manifest[0]["sha256"]), 64)

    def test_dedup_merges_title_match_and_preserves_doi(self):
        base = {
            "seed_id": "CEV2022", "direction": "backward", "work_id": "ref1",
            "title": "A Survey of Research on Retail Central Bank Digital Currency",
            "year": "2020", "decision": "RETAIN_CBDC_PREDECESSOR",
            "c001_impact": "CHECKS_PRE_CEV_CBDC_SCOPE", "metadata_status": "REFERENCE_METADATA_ONLY",
            "scientific_verification": "NOT_PERFORMED",
        }
        crossref = dict(base, source="crossref_reference_list", doi="")
        openalex = dict(base, source="openalex_works", work_id="W1", doi="10.2139/ssrn.3652492", metadata_status="PUBLIC_METADATA")
        retained = self.module.dedup([crossref, openalex])
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0]["doi"], "10.2139/ssrn.3652492")


if __name__ == "__main__":
    unittest.main()
