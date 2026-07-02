import json
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))


class ProductIntelligenceTests(unittest.TestCase):
    def test_three_manufacturing_profiles_are_distinct_and_draft_only(self):
        from product_intelligence import analyze_product_materials

        packaging = analyze_product_materials(
            {
                "company_location": "东莞",
                "factory_type": "包装厂",
                "product_name": "重型包装纸箱、物流包装、出口包装",
                "product_description": "面向重货、电商仓储和外贸出货的高强度纸箱。",
                "materials": ["高强瓦楞纸", "加厚纸板"],
                "factory_capabilities": ["定制尺寸", "印刷", "抗压", "出口包装"],
                "typical_customers": ["电商仓储", "制造工厂", "物流公司", "外贸企业"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
            }
        )
        fitness = analyze_product_materials(
            {
                "company_location": "东莞",
                "factory_type": "健身器材厂",
                "product_name": "哑铃、力量训练器材、家用健身器材",
                "product_description": "面向家用、商用和团购客户的力量训练产品。",
                "materials": ["钢材", "橡胶包胶", "可调节结构"],
                "factory_capabilities": ["OEM/ODM", "定制颜色", "批量供货"],
                "typical_customers": ["健身房", "经销商", "跨境卖家", "团购客户"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
            }
        )
        electronics = analyze_product_materials(
            {
                "company_location": "东莞",
                "factory_type": "电子配件厂",
                "product_name": "电子连接件、线束、充电配件",
                "product_description": "面向电子厂、品牌商和维修渠道的电子配件。",
                "materials": ["铜件", "塑胶外壳", "线材"],
                "factory_capabilities": ["打样", "小批量", "批量生产", "定制规格"],
                "typical_customers": ["电子厂", "品牌商", "跨境卖家", "维修渠道"],
                "platforms": ["小红书", "抖音", "公众号"],
                "mode": "draft_only",
            }
        )

        packaging_text = json.dumps(packaging, ensure_ascii=False)
        fitness_text = json.dumps(fitness, ensure_ascii=False)
        electronics_text = json.dumps(electronics, ensure_ascii=False)

        self.assertEqual(packaging["next_growth_inputs"]["mode"], "draft_only")
        self.assertIn("抗压", packaging_text)
        self.assertIn("电商仓储", packaging_text)
        self.assertIn("包胶", fitness_text)
        self.assertIn("健身房", fitness_text)
        self.assertIn("打样", electronics_text)
        self.assertIn("品牌商", electronics_text)
        self.assertNotIn("健身房", packaging_text)
        self.assertNotIn("纸箱", electronics_text)

    def test_missing_information_is_reported_without_fabrication(self):
        from product_intelligence import analyze_product_materials

        output = analyze_product_materials(
            {
                "company_location": "东莞",
                "factory_type": "五金厂",
                "product_name": "五金定制件",
                "product_description": "",
                "materials": [],
                "factory_capabilities": [],
                "certifications": [],
                "delivery_cycle": "",
                "price_range": "",
                "typical_customers": [],
                "platforms": ["小红书", "抖音"],
                "mode": "draft_only",
            }
        )

        missing = "；".join(output["missing_information"])
        self.assertIn("材料", missing)
        self.assertIn("工厂能力", missing)
        self.assertIn("认证", missing)
        self.assertIn("交期", missing)
        self.assertIn("价格", missing)
        self.assertIn("典型客户", missing)
        self.assertNotIn("ISO9001", json.dumps(output, ensure_ascii=False))
        self.assertEqual(output["next_growth_inputs"]["mode"], "draft_only")

    def test_writes_case_outputs_for_downstream_growth(self):
        from product_intelligence import analyze_product_materials, write_case_outputs

        tmp_root = Path(self.id().split(".")[-1])
        if tmp_root.exists():
            import shutil

            shutil.rmtree(tmp_root)
        try:
            output = analyze_product_materials(
                {
                    "company_location": "东莞",
                    "factory_type": "包装厂",
                    "product_name": "重型包装纸箱、物流包装、出口包装",
                    "materials": ["高强瓦楞纸"],
                    "factory_capabilities": ["抗压", "出口包装"],
                    "typical_customers": ["电商仓储"],
                    "platforms": ["小红书", "抖音", "公众号"],
                    "mode": "draft_only",
                }
            )
            paths = write_case_outputs(tmp_root, output)

            for key in ("product_profile", "product_card", "growth_input", "summary"):
                self.assertTrue(Path(paths[key]).exists(), key)
            growth_input = json.loads(Path(paths["growth_input"]).read_text(encoding="utf-8"))
            self.assertIn("product_profile", growth_input)
            self.assertEqual(growth_input["mode"], "draft_only")
            self.assertIn("产品资料卡", Path(paths["product_card"]).read_text(encoding="utf-8"))
        finally:
            if tmp_root.exists():
                import shutil

                shutil.rmtree(tmp_root)


if __name__ == "__main__":
    unittest.main()
