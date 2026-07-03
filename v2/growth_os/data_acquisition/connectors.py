from __future__ import annotations

from typing import Any

from .evidence import Evidence, create_evidence
from .normalizer import normalize_company_record


def build_manual_url_evidence(items: list[dict[str, Any]], source_id: str = "manual_url_import") -> list[Evidence]:
    evidence: list[Evidence] = []
    for item in items:
        url = str(item.get("url") or "").strip()
        title = str(item.get("title") or "公开来源").strip()
        excerpt = str(item.get("excerpt") or item.get("snippet") or "").strip()
        if not url:
            continue
        evidence.append(
            create_evidence(
                source_id=source_id,
                url=url,
                raw_excerpt=f"{title}：{excerpt}",
                is_public=True,
                allowed_for_marketing=False,
                notes="公开来源仅作为研究证据，营销引用需人工复核。",
            )
        )
    return evidence


def build_sandbox_company_leads(
    *,
    product_name: str,
    target_customers: list[str],
    evidence_items: list[Evidence],
    location: str = "东莞",
) -> list[dict[str, Any]]:
    source_refs = [item.evidence_id for item in evidence_items] or ["unverified"]
    leads: list[dict[str, Any]] = []
    for index, customer in enumerate(target_customers[:6] or ["制造工厂", "电商仓储", "物流公司"], start=1):
        raw = {
            "company_name": f"{location}{customer}样例线索 {index}",
            "location": location,
            "industry": customer,
            "source_refs": source_refs[:2],
            "matched_product": product_name,
            "buying_signal": f"与{product_name}存在采购或内容验证场景，需人工核验。",
            "score": 76 - index,
            "contact_status": "unknown",
            "next_action": "进入人工公开来源复核，不自动触达。",
            "risk_notes": ["沙盒线索，不代表真实客户；无公开联系方式时标记 unknown。"],
            "status": "unverified",
        }
        leads.append(normalize_company_record(raw, matched_product=product_name).to_dict())
    return leads

