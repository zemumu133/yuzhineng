from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def evidence_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass
class Evidence:
    evidence_id: str
    source_id: str
    url: str = ""
    file_path: str = ""
    captured_at: str = field(default_factory=now_iso)
    is_public: bool = True
    is_user_authorized: bool = False
    allowed_for_marketing: bool = False
    raw_excerpt: str = ""
    hash: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.url and not self.file_path:
            raise ValueError("Evidence requires url or file_path")
        if not self.hash:
            self.hash = evidence_hash(f"{self.source_id}|{self.url}|{self.file_path}|{self.raw_excerpt}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_evidence(
    *,
    source_id: str,
    url: str = "",
    file_path: str = "",
    raw_excerpt: str = "",
    is_public: bool = True,
    is_user_authorized: bool = False,
    allowed_for_marketing: bool = False,
    notes: str = "",
) -> Evidence:
    return Evidence(
        evidence_id=f"ev_{uuid4().hex[:16]}",
        source_id=source_id,
        url=url,
        file_path=file_path,
        raw_excerpt=raw_excerpt,
        is_public=is_public,
        is_user_authorized=is_user_authorized,
        allowed_for_marketing=allowed_for_marketing,
        notes=notes,
    )

