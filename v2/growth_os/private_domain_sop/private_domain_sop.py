from __future__ import annotations

from typing import Any


def build_private_domain_sop(product_profile: dict[str, Any], lead_research: dict[str, Any]) -> dict[str, Any]:
    product = product_profile.get("product_name") or product_profile.get("product") or "制造业产品"
    return {
        "stages": [
            {"name": "公开来源复核", "owner": "运营/销售", "rule": "确认来源公开、有效、与产品匹配。"},
            {"name": "轻触达准备", "owner": "销售", "rule": "只使用审批通过的评论/私信/邮件草稿。"},
            {"name": "需求澄清", "owner": "销售", "rule": "记录规格、数量、交期、认证，不索取私人敏感信息。"},
            {"name": "工厂交接", "owner": "老板/销售负责人", "rule": "确认报价边界、样品、产能和发货周期。"},
        ],
        "comment_reply_drafts": [
            {"target": "公开评论", "draft": f"可以先按使用场景、规格和数量评估{product}方案，我们整理了一个采购清单供人工确认后参考。", "status": "draft_only"}
        ],
        "dm_drafts": [
            {"target": "意向用户", "draft": f"您好，我们可以先按规格、数量、交期帮您梳理{product}需求清单。本消息仅为草稿，发送前需人工确认。", "status": "draft_only"}
        ],
        "followup_tasks": [
            {"title": "人工复核高分线索来源", "owner": "销售", "status": "pending"},
            {"title": "整理产品图片、工艺、产能和认证材料", "owner": "工厂", "status": "pending"},
        ],
    }

