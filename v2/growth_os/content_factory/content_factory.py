from __future__ import annotations

from typing import Any


def _product_name(product_profile: dict[str, Any]) -> str:
    return str(product_profile.get("product_name") or product_profile.get("product") or "制造业产品")


def build_content_drafts(product_profile: dict[str, Any], lead_research: dict[str, Any]) -> dict[str, Any]:
    product = _product_name(product_profile)
    customer_types = [lead.get("industry", "目标客户") for lead in lead_research.get("lead_candidates", [])[:3]]
    customer_text = "、".join(customer_types) or "目标客户"
    return {
        "xiaohongshu_notes": [
            {"title": f"{product}采购避坑：先看这 4 个点", "summary": f"面向{customer_text}，讲清规格、承重、交期和验收。", "status": "draft_only"},
            {"title": f"工厂老板怎么判断{product}供应商靠不靠谱", "summary": "用交付流程和质检清单降低采购顾虑。", "status": "draft_only"},
            {"title": f"{product}询价前要准备哪些资料", "summary": "引导客户准备尺寸、数量、场景和交期。", "status": "draft_only"},
        ],
        "douyin_scripts": [
            {"title": f"{product}一分钟采购说明", "hook": "同样报价，为什么交付风险差很多？", "status": "draft_only"},
            {"title": f"{product}工厂实拍脚本", "hook": "从材料、工艺到发货，给采购一个判断清单。", "status": "draft_only"},
        ],
        "wechat_article_outline": [
            {"title": f"{product}供应商选择 SOP", "summary": "从需求澄清、打样、报价、验收、复盘五步展开。", "status": "draft_only"}
        ],
        "sales_talk_track": [
            "先确认使用场景、规格、数量、交期和认证要求。",
            "只给出人工核实后的报价和交期，不做夸大承诺。",
        ],
    }

