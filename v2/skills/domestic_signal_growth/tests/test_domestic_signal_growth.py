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

    def test_dongguan_manufacturing_output_has_productized_workflow_fields(self):
        from domestic_signal_growth import generate_signal_report

        output = generate_signal_report(
            {
                "company_location": "东莞",
                "factory_type": "包装厂",
                "product_name": "重型包装纸箱、物流包装、出口包装",
                "product_description": "面向重货、电商仓储和外贸出货的高强度纸箱。",
                "factory_capabilities": ["重型瓦楞纸箱定制", "出口包装", "打样"],
                "target_customer_hint": ["电商仓储", "制造工厂", "物流公司", "外贸企业"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
                "search_required": True,
            },
            searcher=FakeSearcher(),
        )

        required_fields = [
            "product_understanding",
            "opportunity_discovery",
            "target_customer_segments",
            "public_sources",
            "content_materials",
            "social_publish_plan",
            "comment_reply_drafts",
            "dm_drafts",
            "account_nurturing_plan",
            "factory_handoff_sheet",
        ]
        for field in required_fields:
            self.assertIn(field, output)
        self.assertEqual(output["mode"], "draft_only")
        self.assertEqual(output["industry"], "包装厂")
        self.assertEqual(output["product_understanding"]["factory_type"], "包装厂")
        self.assertIn("销售交接单", output["factory_handoff_sheet"]["handoff_title"])
        self.assertTrue(output["factory_handoff_sheet"]["requires_human_review"])

    def test_packaging_fitness_and_electronics_manufacturing_templates_are_distinct(self):
        from domestic_signal_growth import generate_signal_report

        cases = [
            {
                "factory_type": "包装厂",
                "product_name": "重型包装纸箱",
                "target_customer_hint": ["电商仓储", "制造工厂", "物流公司"],
            },
            {
                "factory_type": "健身器材厂",
                "product_name": "哑铃、力量训练器材、家用健身器材",
                "target_customer_hint": ["健身房", "经销商", "跨境卖家"],
            },
            {
                "factory_type": "电子配件厂",
                "product_name": "电子连接件、线束、充电配件",
                "target_customer_hint": ["电子厂", "品牌商", "跨境卖家", "维修渠道"],
            },
        ]
        outputs = [
            generate_signal_report(
                {
                    "company_location": "东莞",
                    "platforms": ["小红书", "抖音", "公众号"],
                    "mode": "draft_only",
                    "search_required": True,
                    **case,
                },
                searcher=FakeSearcher(),
            )
            for case in cases
        ]

        packaging_text = jsonish(outputs[0])
        fitness_text = jsonish(outputs[1])
        electronics_text = jsonish(outputs[2])

        self.assertIn("承重", packaging_text)
        self.assertIn("货损", packaging_text)
        self.assertIn("空间", fitness_text)
        self.assertIn("经销商", fitness_text)
        self.assertIn("线束", electronics_text)
        self.assertIn("品牌商", electronics_text)
        self.assertNotIn("健身房", electronics_text)
        self.assertNotIn("哑铃", electronics_text)
        self.assertNotIn("健身房", packaging_text)
        self.assertNotIn("纸箱", electronics_text)

    def test_product_profile_from_product_intelligence_is_used_first(self):
        from domestic_signal_growth import generate_signal_report

        output = generate_signal_report(
            {
                "company_location": "东莞",
                "factory_type": "包装厂",
                "product_name": "旧产品名不应优先",
                "target_customer_hint": ["电商仓储"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
                "search_required": True,
                "product_profile": {
                    "product_name": "高强防潮出口纸箱",
                    "factory_type": "包装厂",
                    "location": "东莞",
                    "category": "重型包装与物流包装",
                    "summary": "适合重货出口和潮湿运输环境的高强包装。",
                    "main_specs": ["五层瓦楞", "可定制尺寸"],
                    "materials": ["高强瓦楞纸", "防潮涂层"],
                    "certifications": ["待人工确认"],
                    "delivery_notes": "打样后确认交期",
                },
            },
            searcher=FakeSearcher(),
        )

        understanding = output["product_understanding"]
        self.assertEqual(output["product"], "高强防潮出口纸箱")
        self.assertEqual(understanding["product_name"], "高强防潮出口纸箱")
        self.assertEqual(understanding["product_profile_source"], "product_intelligence")
        self.assertEqual(understanding["category"], "重型包装与物流包装")
        self.assertIn("防潮涂层", understanding["materials"])
        self.assertIn("五层瓦楞", understanding["main_specs"])
        self.assertIn("防潮", jsonish(output["content_materials"]))


def jsonish(value):
    import json

    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
