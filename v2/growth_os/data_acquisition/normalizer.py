from __future__ import annotations

from typing import Any

from .lead_models import CompanyLead


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def normalize_company_record(record: dict[str, Any], *, matched_product: str = "") -> CompanyLead:
    source_refs = _as_list(record.get("source_refs") or record.get("sources") or record.get("evidence_refs"))
    score = record.get("score")
    if score is None:
        score = 55 + min(25, len(source_refs) * 10)
    return CompanyLead(
        company_name=str(record.get("company_name") or record.get("name") or "未命名公司").strip(),
        location=str(record.get("location") or "unknown").strip(),
        industry=str(record.get("industry") or "unknown").strip(),
        source_refs=source_refs,
        matched_product=str(record.get("matched_product") or matched_product or "unknown").strip(),
        buying_signal=str(record.get("buying_signal") or record.get("signal") or "unknown").strip(),
        score=int(score),
        contact_status=str(record.get("contact_status") or "unknown").strip(),
        next_action=str(record.get("next_action") or "人工复核公开来源和需求匹配度").strip(),
        risk_notes=_as_list(record.get("risk_notes")),
        status=str(record.get("status") or "unverified").strip(),
    )

