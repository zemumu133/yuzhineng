from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OpenClaw")
WEB_SEARCH_DIR = ROOT / "v2" / "client-shell" / "lobsterai" / "src" / "SKILLs" / "web-search"
CONNECTION_CACHE = WEB_SEARCH_DIR / ".connection"
DEFAULT_LOBSTER_WEB_SEARCH = "http://127.0.0.1:8923"
DEFAULT_SEARXNG = "http://127.0.0.1:8080"
CN_TZ = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(CN_TZ).isoformat(timespec="seconds")


def is_public_http_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value or "", re.I))


class SearchAdapter:
    """Small public-source search adapter for domestic_signal_growth.

    It never invents URLs. When no provider returns public sources it reports
    `source_status=unverified` or `search_failed`.
    """

    def __init__(
        self,
        lobster_base_url: str | None = None,
        searxng_base_url: str | None = None,
        timeout_seconds: int = 45,
    ) -> None:
        self.lobster_base_url = (lobster_base_url or os.environ.get("LOBSTER_WEB_SEARCH_BASE_URL") or DEFAULT_LOBSTER_WEB_SEARCH).rstrip("/")
        self.searxng_base_url = (searxng_base_url or os.environ.get("SEARXNG_BASE_URL") or DEFAULT_SEARXNG).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def search(
        self,
        query: str,
        max_results: int = 5,
        manual_seed_urls: list[Any] | None = None,
        provider_mode: str = "existing_lobster_web_search",
    ) -> dict[str, Any]:
        provider_mode = provider_mode or "existing_lobster_web_search"
        if provider_mode == "manual_seed_urls":
            return self._manual_seed_sources(query, manual_seed_urls)
        if provider_mode == "no_source_available":
            return self._empty_result(query, provider_mode, "用户或系统选择不使用公开搜索。", "unverified")

        attempts: list[dict[str, Any]] = []
        if manual_seed_urls:
            manual = self._manual_seed_sources(query, manual_seed_urls)
            attempts.extend(manual["attempts"])
            if manual["sources"]:
                manual["provider"] = "manual_seed_urls"
                return manual

        if provider_mode in {"existing_lobster_web_search", "browser_public_search"}:
            bridge = self._lobster_bridge_search(query, max_results=max_results, provider_label=provider_mode)
            attempts.extend(bridge["attempts"])
            if bridge["sources"]:
                bridge["attempts"] = attempts
                return bridge
            if bridge["source_status"] == "search_failed":
                return bridge

        searxng = self._searxng_search(query, max_results=max_results)
        attempts.extend(searxng["attempts"])
        if searxng["sources"]:
            searxng["attempts"] = attempts
            return searxng

        return {
            "provider": provider_mode,
            "query": query,
            "source_status": "unverified",
            "sources": [],
            "errors": bridge.get("errors", []) if "bridge" in locals() else [],
            "attempts": attempts,
            "fetched_at": now_iso(),
        }

    def _lobster_bridge_search(self, query: str, max_results: int, provider_label: str) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        errors: list[str] = []

        health = self._http_get_json(f"{self.lobster_base_url}/api/health")
        attempts.append({"provider": "existing_lobster_web_search", "step": "health", "ok": health.get("success") is True})
        if health.get("success") is not True:
            errors.append(f"web-search bridge health failed: {health.get('error') or health}")
            return self._search_result(provider_label, query, [], "search_failed", errors, attempts)

        connection_id = self._read_cached_connection_id()
        for round_index in range(2):
            if not connection_id:
                connection_id = self._connect_bridge(attempts, errors)
            if not connection_id:
                break
            response = self._post_json(
                f"{self.lobster_base_url}/api/search",
                {
                    "connectionId": connection_id,
                    "query": query,
                    "maxResults": max_results,
                    "engine": os.environ.get("WEB_SEARCH_ENGINE", "auto"),
                },
            )
            ok = response.get("success") is True
            attempts.append({"provider": "existing_lobster_web_search", "step": f"search_round_{round_index + 1}", "ok": ok})
            if ok:
                data = response.get("data") or {}
                sources = self._normalize_lobster_sources(data.get("results") or [], provider_label)
                status = "verified_public_sources" if sources else "unverified"
                return self._search_result(provider_label, query, sources, status, errors, attempts, raw_meta=data)

            error_text = str(response.get("error") or response)
            errors.append(error_text)
            if self._is_stale_connection_error(error_text):
                self._clear_connection_cache()
                connection_id = self._connect_bridge(attempts, errors)
                continue
            break

        status = "search_failed" if errors else "unverified"
        return self._search_result(provider_label, query, [], status, errors, attempts)

    def _connect_bridge(self, attempts: list[dict[str, Any]], errors: list[str]) -> str | None:
        launch = self._post_json(f"{self.lobster_base_url}/api/browser/launch", {})
        attempts.append({"provider": "existing_lobster_web_search", "step": "browser_launch", "ok": launch.get("success") is True})
        if launch.get("success") is not True:
            errors.append(f"browser launch failed: {launch.get('error') or launch}")
            return None
        connect = self._post_json(f"{self.lobster_base_url}/api/browser/connect", {})
        attempts.append({"provider": "existing_lobster_web_search", "step": "browser_connect", "ok": connect.get("success") is True})
        if connect.get("success") is not True:
            errors.append(f"browser connect failed: {connect.get('error') or connect}")
            return None
        connection_id = ((connect.get("data") or {}).get("connectionId") or "").strip()
        if connection_id:
            try:
                CONNECTION_CACHE.write_text(connection_id, encoding="utf-8")
            except OSError:
                pass
            return connection_id
        errors.append("browser connect did not return connectionId")
        return None

    def _searxng_search(self, query: str, max_results: int) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        errors: list[str] = []
        url = f"{self.searxng_base_url}/search?q={urllib.parse.quote(query)}&format=json"
        response = self._http_get_json(url)
        ok = bool(response.get("results"))
        attempts.append({"provider": "searxng", "step": "search", "ok": ok})
        if not ok:
            if response.get("error"):
                errors.append(f"searxng unavailable: {response['error']}")
            return self._search_result("searxng", query, [], "unverified", errors, attempts)
        sources = []
        for item in (response.get("results") or [])[:max_results]:
            url_value = item.get("url") or ""
            if not is_public_http_url(url_value):
                continue
            sources.append(
                {
                    "title": self._clean_text(item.get("title") or url_value),
                    "url": url_value,
                    "snippet": self._clean_text(item.get("content") or ""),
                    "provider": "searxng",
                    "fetched_at": now_iso(),
                    "source_type": "public_web",
                }
            )
        status = "verified_public_sources" if sources else "unverified"
        return self._search_result("searxng", query, sources, status, errors, attempts)

    def _manual_seed_sources(self, query: str, manual_seed_urls: list[Any] | None) -> dict[str, Any]:
        sources = []
        for index, item in enumerate(manual_seed_urls or [], start=1):
            if isinstance(item, str):
                url_value = item
                title = item
                snippet = ""
            elif isinstance(item, dict):
                url_value = str(item.get("url") or "")
                title = str(item.get("title") or url_value or f"人工来源 {index}")
                snippet = str(item.get("snippet") or item.get("source_excerpt") or "")
            else:
                continue
            if not is_public_http_url(url_value):
                continue
            sources.append(
                {
                    "title": self._clean_text(title),
                    "url": url_value,
                    "snippet": self._clean_text(snippet),
                    "provider": "manual_seed_urls",
                    "fetched_at": now_iso(),
                    "source_type": "public_web",
                }
            )
        status = "verified_public_sources" if sources else "unverified"
        return self._search_result("manual_seed_urls", query, sources, status, [], [{"provider": "manual_seed_urls", "ok": bool(sources)}])

    def _normalize_lobster_sources(self, results: list[dict[str, Any]], provider_label: str) -> list[dict[str, Any]]:
        sources = []
        seen: set[str] = set()
        for item in results:
            url_value = str(item.get("url") or "")
            if not is_public_http_url(url_value) or url_value in seen:
                continue
            seen.add(url_value)
            sources.append(
                {
                    "title": self._clean_text(item.get("title") or url_value),
                    "url": url_value,
                    "snippet": self._clean_text(item.get("snippet") or ""),
                    "provider": provider_label,
                    "fetched_at": now_iso(),
                    "source_type": "public_web",
                }
            )
        return sources

    def _search_result(
        self,
        provider: str,
        query: str,
        sources: list[dict[str, Any]],
        source_status: str,
        errors: list[str],
        attempts: list[dict[str, Any]],
        raw_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "provider": provider,
            "query": query,
            "source_status": source_status,
            "sources": sources,
            "errors": errors,
            "attempts": attempts,
            "fetched_at": now_iso(),
            "raw_meta": raw_meta or {},
        }

    def _empty_result(self, query: str, provider: str, reason: str, source_status: str) -> dict[str, Any]:
        return self._search_result(provider, query, [], source_status, [reason], [{"provider": provider, "ok": False, "reason": reason}])

    def _read_cached_connection_id(self) -> str | None:
        env_id = (os.environ.get("LOBSTER_WEB_SEARCH_CONNECTION_ID") or "").strip()
        if env_id:
            return env_id
        try:
            if CONNECTION_CACHE.exists():
                value = CONNECTION_CACHE.read_text(encoding="utf-8").strip()
                return value or None
        except OSError:
            return None
        return None

    def _clear_connection_cache(self) -> None:
        try:
            CONNECTION_CACHE.unlink(missing_ok=True)
        except OSError:
            pass

    def _http_get_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(url, method="GET")
        return self._send_json(request)

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        return self._send_json(request)

    def _send_json(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": raw or str(exc)}
            payload.setdefault("success", False)
            return payload
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _is_stale_connection_error(self, error_text: str) -> bool:
        lowered = error_text.lower()
        return any(
            marker in lowered
            for marker in [
                "connection not found",
                "connection not active",
                "connection became invalid",
                "target page",
                "browser has been closed",
                "failed to connect to cdp",
            ]
        )

    def _clean_text(self, value: Any) -> str:
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        return text[:500]


def search_public_sources(query: str, max_results: int = 5, **kwargs: Any) -> dict[str, Any]:
    return SearchAdapter().search(query, max_results=max_results, **kwargs)
