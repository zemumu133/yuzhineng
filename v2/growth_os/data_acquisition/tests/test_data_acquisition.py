import unittest

from growth_os.data_acquisition.connectors import build_manual_url_evidence, build_sandbox_company_leads
from growth_os.data_acquisition.data_source_registry import default_registry


class DataAcquisitionTests(unittest.TestCase):
    def test_default_registry_has_safe_public_sources(self):
        registry = default_registry()
        public_ids = {source.source_id for source in registry.public_sources()}
        self.assertIn("manual_url_import", public_ids)
        self.assertIn("public_web_search", public_ids)

    def test_evidence_and_leads_are_traceable(self):
        evidence = build_manual_url_evidence(
            [{"url": "https://example.com/public", "title": "公开页面", "excerpt": "公开摘要"}]
        )
        leads = build_sandbox_company_leads(
            product_name="重型包装纸箱",
            target_customers=["电商仓储"],
            evidence_items=evidence,
        )
        self.assertEqual(len(evidence), 1)
        self.assertEqual(leads[0]["contact_status"], "unknown")
        self.assertTrue(leads[0]["source_refs"])


if __name__ == "__main__":
    unittest.main()
