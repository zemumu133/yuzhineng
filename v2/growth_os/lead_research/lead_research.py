from __future__ import annotations

from typing import Any

from growth_os.data_acquisition.connectors import build_manual_url_evidence, build_sandbox_company_leads


def build_lead_research(
    *,
    product_profile: dict[str, Any],
    target_customers: list[str],
    public_sources: list[dict[str, Any]] | None = None,
    location: str = "东莞",
) -> dict[str, Any]:
    product_name = (
        product_profile.get("product_name")
        or product_profile.get("product")
        or product_profile.get("name")
        or "制造业产品"
    )
    evidence = build_manual_url_evidence(public_sources or [])
    leads = build_sandbox_company_leads(
        product_name=product_name,
        target_customers=target_customers,
        evidence_items=evidence,
        location=location,
    )
    return {
        "product_name": product_name,
        "location": location,
        "sources": public_sources or [],
        "evidence": [item.to_dict() for item in evidence],
        "lead_candidates": leads,
        "source_status": "public_sources_available" if public_sources else "sandbox_sources_only",
        "safety_notes": [
            "本层只整理公开来源和沙盒线索，不登录平台，不采集私人联系方式。",
            "没有公开联系方式时 contact_status 必须为 unknown。",
        ],
    }

