import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))


class FakeSearcher:
    def __init__(self, sources=None, status="verified_public_sources"):
        self.sources = sources if sources is not None else [
            {
                "title": "公开测试来源",
                "url": "https://example.com/public",
                "snippet": "公开网页摘要",
                "provider": "manual_seed_urls",
                "fetched_at": "2026-07-02T00:00:00+08:00",
                "source_type": "public_web",
            }
        ]
        self.status = status
        self.last_query = None

    def search(self, query, max_results=5, manual_seed_urls=None, provider_mode="manual_seed_urls"):
        self.last_query = query
        return {
            "provider": "manual_seed_urls",
            "query": query,
            "source_status": self.status,
            "sources": self.sources,
            "errors": [],
            "attempts": [{"provider": "manual_seed_urls", "ok": bool(self.sources)}],
        }


class DomesticSignalGrowthTests(unittest.TestCase):
    def test_certificate_training_schema_and_sources(self):
        from domestic_signal_growth import generate_signal_report

        payload = {
            "product": "职业证书考评服务",
            "industry": "教育培训",
            "target_customers": ["培训机构", "人力资源公司"],
            "platforms": ["小红书", "抖音"],
            "mode": "draft_only",
            "search_required": True,
        }
        output = generate_signal_report(payload, searcher=FakeSearcher())

        self.assertEqual(output["mode"], "draft_only")
        self.assertEqual(output["source_status"], "verified_public_sources")
        self.assertGreaterEqual(len(output["sources"]), 1)
        self.assertIn("opportunity_judgement", output)
        self.assertIn("target_customer_types", output)
        self.assertIn("platform_strategy", output)
        self.assertIn("followup_drafts", output)
        self.assertTrue(all(item["requires_approval"] for item in output["todos"]))

    def test_industries_are_not_all_certificate_templates(self):
        from domestic_signal_growth import generate_signal_report

        packaging = generate_signal_report(
            {
                "product": "重型包装纸箱服务",
                "industry": "包装制造 / 仓储物流",
                "target_customers": ["电商仓储", "工厂", "物流公司"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
                "search_required": True,
            },
            searcher=FakeSearcher(),
        )
        fitness = generate_signal_report(
            {
                "product": "健身器材",
                "industry": "健身器材 / 商贸",
                "target_customers": ["健身房", "经销商", "跨境卖家"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
                "search_required": True,
            },
            searcher=FakeSearcher(),
        )

        packaging_text = str(packaging["target_customer_types"]) + str(packaging["platform_strategy"])
        fitness_text = str(fitness["target_customer_types"]) + str(fitness["platform_strategy"])

        self.assertIn("破损", packaging_text)
        self.assertIn("仓储", packaging_text)
        self.assertNotIn("证书考评", packaging_text)
        self.assertIn("健身房", fitness_text)
        self.assertIn("经销商", fitness_text)
        self.assertNotIn("证书考评", fitness_text)

    def test_no_sources_are_reported_as_unverified_without_fake_urls(self):
        from domestic_signal_growth import generate_signal_report

        output = generate_signal_report(
            {
                "product": "重型包装纸箱服务",
                "industry": "包装制造 / 仓储物流",
                "target_customers": ["电商仓储"],
                "platforms": ["小红书"],
                "mode": "draft_only",
                "search_required": True,
            },
            searcher=FakeSearcher(sources=[], status="unverified"),
        )

        self.assertEqual(output["source_status"], "unverified")
        self.assertEqual(output["sources"], [])
        self.assertTrue(any("没有真实公开来源" in note for note in output["risk_notes"]))


if __name__ == "__main__":
    unittest.main()
