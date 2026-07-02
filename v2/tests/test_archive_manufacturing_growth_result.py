import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(r"D:\OpenClaw")
SCRIPT = ROOT / "v2" / "scripts" / "archive_manufacturing_growth_result.py"


def load_archive_module():
    spec = importlib.util.spec_from_file_location("archive_manufacturing_growth_result", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArchiveManufacturingGrowthResultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="phase2c-archive-test-"))
        self.input_dir = self.tmp / "task-output"
        self.projects_root = self.tmp / "projects"
        self.input_dir.mkdir()

        skill_output = {
            "product": "电子连接件、线束、充电配件",
            "industry": "电子配件厂",
            "city": "东莞",
            "mode": "draft_only",
            "source_status": "verified_public_sources",
            "sources": [
                {
                    "title": "公开来源 A",
                    "url": "https://example.com/a",
                    "snippet": "公开页面摘要",
                    "provider": "manual_seed_urls",
                }
            ],
            "product_understanding": {
                "location": "东莞",
                "factory_type": "电子配件厂",
                "product_name": "电子连接件、线束、充电配件",
                "product_description": "面向电子厂和品牌商的电子配件。",
                "factory_capabilities": ["线束打样", "连接件加工"],
                "selling_points": ["规格匹配", "打样速度"],
                "suitable_customer_types": ["电子厂和组装厂", "品牌商"],
            },
            "opportunity_discovery": {
                "opportunity_score": 78,
                "public_demand_signals": ["发布新品量产信息"],
            },
            "target_customer_segments": [
                {"type": "电子厂和组装厂", "pain_points": ["规格匹配耗时"], "decision_makers": ["采购经理"]}
            ],
            "content_materials": {
                "xiaohongshu_notes": ["线束采购前要确认的 5 个参数"],
                "douyin_scripts": ["30 秒看懂线束打样流程"],
                "wechat_article_outline": ["电子连接件询价清单模板"],
                "product_intro_copy": "电子连接件适合关注规格匹配的客户。",
            },
            "comment_reply_drafts": [{"intent": "询价", "draft": "先确认规格、数量和使用场景。"}],
            "dm_drafts": [{"scenario": "客户表达采购兴趣", "draft": "先整理规格和交期，再人工跟进。"}],
            "account_nurturing_plan": {
                "account_positioning": "东莞电子配件工厂账号",
                "industry_keywords": ["东莞电子配件厂", "线束加工"],
            },
            "factory_handoff_sheet": {
                "handoff_title": "电子配件客户交接单",
                "recommended_owner": "工厂销售或老板",
                "qualification_questions": ["是否有图纸、样品或 BOM？"],
            },
            "todos": [{"title": "人工复核规格和交期", "owner": "human", "requires_approval": True}],
            "risk_notes": ["不得虚构认证或客户品牌合作。"],
            "next_steps": ["人工复核来源和素材。"],
        }
        (self.input_dir / "skill_output.json").write_text(
            json.dumps(skill_output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.input_dir / "input.json").write_text(
            json.dumps(
                {
                    "company_location": "东莞",
                    "factory_type": "电子配件厂",
                    "product_name": "电子连接件、线束、充电配件",
                    "target_customer_hint": ["电子厂", "品牌商"],
                    "platforms": ["小红书", "抖音", "公众号"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (self.input_dir / "safety_check.json").write_text(
            json.dumps({"external_action_mode": "draft_only", "real_external_send": False}, ensure_ascii=False),
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_archives_task_output_into_project_workspace_and_index(self):
        archive = load_archive_module()

        result = archive.archive_task_output(
            self.input_dir,
            projects_root=self.projects_root,
            project_slug="dongguan-electronics-parts",
            created_at="2026-07-02T17:30:00+08:00",
        )

        project_dir = Path(result["project_dir"])
        self.assertTrue(project_dir.name.startswith("20260702-173000-dongguan-electronics-parts"))
        self.assertTrue((project_dir / "input.json").exists())
        self.assertTrue((project_dir / "project_manifest.json").exists())
        self.assertTrue((project_dir / "sources.json").exists())
        self.assertTrue((project_dir / "skill_output.json").exists())
        self.assertTrue((project_dir / "report.md").exists())
        self.assertTrue((project_dir / "handoff.docx").exists())
        self.assertTrue((project_dir / "todos.json").exists())
        self.assertTrue((project_dir / "safety_check.json").exists())
        self.assertTrue((project_dir / "README_CN.md").exists())

        manifest = json.loads((project_dir / "project_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["mode"], "draft_only")
        self.assertEqual(manifest["source_status"], "verified_public_sources")
        self.assertEqual(manifest["safety_status"]["real_external_send"], False)
        self.assertTrue(Path(manifest["generated_files"]["report_md"]).exists())
        self.assertTrue(Path(manifest["generated_files"]["handoff_docx"]).exists())

        report_text = (project_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("draft_only", report_text)
        self.assertIn("小红书内容建议", report_text)
        self.assertIn("工厂销售交接建议", report_text)

        self.assertTrue(zipfile.is_zipfile(project_dir / "handoff.docx"))
        self.assertGreater((project_dir / "handoff.docx").stat().st_size, 1000)

        index = json.loads((self.projects_root / "projects_index.json").read_text(encoding="utf-8"))
        self.assertEqual(len(index), 1)
        self.assertEqual(index[0]["mode"], "draft_only")
        self.assertEqual(index[0]["source_count"], 1)
        self.assertIn("report.md", (self.projects_root / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
