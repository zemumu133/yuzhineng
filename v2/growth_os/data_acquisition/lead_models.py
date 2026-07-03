from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CompanyLead:
    company_name: str
    location: str
    industry: str
    source_refs: list[str]
    matched_product: str
    buying_signal: str
    score: int
    contact_status: str
    next_action: str
    risk_notes: list[str] = field(default_factory=list)
    status: str = "unverified"

    def __post_init__(self) -> None:
        self.score = max(0, min(100, int(self.score)))
        if not self.source_refs:
            self.status = "unverified"
            self.risk_notes.append("缺少可追溯来源，禁止直接触达。")
        if self.contact_status not in {"unknown", "company_public", "user_provided", "not_collected"}:
            self.contact_status = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

