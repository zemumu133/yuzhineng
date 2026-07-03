from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


SOURCE_TYPES = {
    "excel_csv_import",
    "crm_import",
    "public_website",
    "public_web_search",
    "tender_notice",
    "company_data_api",
    "map_poi_api",
    "social_hotspot_screen_observed",
    "user_authorized_platform_data",
    "manual_url_import",
}


@dataclass
class DataSource:
    source_id: str
    name: str
    source_type: str
    requires_auth: bool
    authorization_status: str
    allowed_fields: list[str]
    usage_policy: str
    rate_limit: str
    enabled: bool
    notes: str = ""

    def __post_init__(self) -> None:
        if self.source_type not in SOURCE_TYPES:
            raise ValueError(f"Unsupported source_type: {self.source_type}")
        if self.requires_auth and self.authorization_status not in {"authorized", "not_authorized", "pending"}:
            raise ValueError("authorization_status must be authorized, not_authorized or pending")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataSourceRegistry:
    def __init__(self, sources: list[DataSource] | None = None) -> None:
        self._sources: dict[str, DataSource] = {}
        for source in sources or []:
            self.register(source)

    def register(self, source: DataSource) -> None:
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> DataSource:
        if source_id not in self._sources:
            raise KeyError(f"Data source not found: {source_id}")
        return self._sources[source_id]

    def enabled_sources(self) -> list[DataSource]:
        return [source for source in self._sources.values() if source.enabled]

    def public_sources(self) -> list[DataSource]:
        return [
            source
            for source in self.enabled_sources()
            if not source.requires_auth and source.source_type in {"public_website", "public_web_search", "tender_notice", "manual_url_import"}
        ]

    def to_list(self) -> list[dict[str, Any]]:
        return [source.to_dict() for source in self._sources.values()]


def default_registry() -> DataSourceRegistry:
    return DataSourceRegistry(
        [
            DataSource(
                source_id="manual_url_import",
                name="人工导入公开 URL",
                source_type="manual_url_import",
                requires_auth=False,
                authorization_status="authorized",
                allowed_fields=["url", "title", "excerpt", "captured_at"],
                usage_policy="只允许用户提供或公开可访问页面，不登录、不绕验证码。",
                rate_limit="manual",
                enabled=True,
                notes="Phase M1 默认可用。",
            ),
            DataSource(
                source_id="public_web_search",
                name="公开网页搜索",
                source_type="public_web_search",
                requires_auth=False,
                authorization_status="authorized",
                allowed_fields=["url", "title", "excerpt", "query"],
                usage_policy="只采集公开网页摘要和来源链接，不采集私人联系方式。",
                rate_limit="low_frequency",
                enabled=True,
                notes="可由现有 web-search bridge 或人工 URL 列表提供。",
            ),
            DataSource(
                source_id="sandbox_csv",
                name="沙盒 CSV 导入",
                source_type="excel_csv_import",
                requires_auth=False,
                authorization_status="authorized",
                allowed_fields=["company_name", "location", "industry", "buying_signal", "source_refs"],
                usage_policy="仅测试或用户自有文件，不代表真实外部抓取。",
                rate_limit="local_file",
                enabled=True,
                notes="Phase M1 测试数据源。",
            ),
        ]
    )

