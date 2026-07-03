from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass
class AuditEvent:
    audit_id: str
    project_id: str
    actor: str
    event: str
    payload: dict[str, Any]
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuditLog:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, *, project_id: str, actor: str, event: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        audit_event = AuditEvent(
            audit_id=f"audit_{uuid4().hex[:16]}",
            project_id=project_id,
            actor=actor,
            event=event,
            payload=payload or {},
        )
        self.events.append(audit_event)
        return audit_event.to_dict()

    def to_list(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.events]

