import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
DEFAULT_OUTPUT = V2 / "packages" / "yuzhineng-pack1-portable-poc"

FORBIDDEN_PARTS = {
    "secrets",
    "logs",
    "backups",
    "data",
    "exports",
    "database",
    "approval_queue",
    "browser_profiles",
    "workspaces",
    "generated_media",
    "restore",
    "node_modules",
    "dist",
    "build",
    ".cache",
    ".vite",
    ".next",
    "coverage",
    "__pycache__",
}

FORBIDDEN_PREFIXES = (
    "v2/projects/",
    "v2/data/",
    "v2/runtimes/",
    "v2/logs/",
    "v2/client-shell/lobsterai/src/",
    "v2/client-shell/lobsterai/openclaw/",
    "v2/client-shell/lobsterai/runtime/",
    "v2/client-shell/lobsterai/openclaw-runtime/",
    "v2/reports/assets/",
)

ALLOWED_PREFIXES = (
    "v2/config/",
    "v2/dev-config/",
    "v2/growth_os/",
    "v2/packaging/",
    "v2/patches/",
    "v2/scripts/",
    "v2/skills/",
    "v2/test-cases/",
    "v2/tests/",
    "v2/workflows/",
)

ALLOWED_REPORTS = (
    "v2/reports/PHASE_M1_1_UI_AGENT_DEDUP_ARCHIVE_REPORT_CN.md",
    "v2/reports/PHASE_PACK1_PORTABLE_POC_REPORT_CN.md",
    "v2/reports/GROWTH_OS_MERGE_PHASE_M1_REPORT_CN.md",
    "v2/reports/YUZHINENG_CURRENT_PROGRESS_REPORT_CN.md",
)


def _rel(path: Path) -> str:
    return path.as_posix().replace("\\", "/")


def run_git(args):
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(ROOT),
            check=True,
            text=True,
            capture_output=True,
        )
        return proc.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        git = Path(r"D:\DevTools\Git\cmd\git.exe")
        if not git.exists():
            raise
        proc = subprocess.run(
            [str(git), *args],
            cwd=str(ROOT),
            check=True,
            text=True,
            capture_output=True,
        )
        return proc.stdout.strip()


def git_files():
    output = run_git(["ls-files"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def current_commit():
    try:
        return run_git(["rev-parse", "HEAD"])
    except Exception:
        return "unknown"


def is_forbidden(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return True
    parts = set(normalized.split("/"))
    if parts & FORBIDDEN_PARTS:
        return True
    lowered = normalized.lower()
    return any(
        lowered.endswith(suffix)
        for suffix in (
            ".env",
            ".key",
            ".token",
            ".pem",
            ".p12",
            ".pfx",
            ".sqlite",
            ".sqlite-wal",
            ".sqlite-shm",
            ".log",
            ".zip",
            ".7z",
            ".rar",
            ".tmp",
        )
    )


def is_allowed(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/")
    if is_forbidden(normalized):
        return False
    if normalized in {"AGENTS.md"}:
        return True
    if normalized.startswith("v2/") and normalized.count("/") == 1 and normalized.endswith(".md"):
        return True
    if normalized in ALLOWED_REPORTS:
        return True
    return normalized.startswith(ALLOWED_PREFIXES)


def clean_output(output_root: Path):
    resolved = output_root.resolve()
    allowed_parent = (V2 / "packages").resolve()
    if allowed_parent not in resolved.parents and resolved != allowed_parent:
        raise ValueError(f"Refusing to remove output outside {allowed_parent}: {resolved}")
    if output_root.exists():
        shutil.rmtree(output_root)


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def package_readme(package_name: str, source_commit: str) -> str:
    return f"""# 宇智能 PACK-1 可移植包 PoC

包名：`{package_name}`

来源 commit：`{source_commit}`

## 这是什么

这是宇智能当前主线能力的可移植恢复包 PoC，用于验证换机恢复路径。它不是正式商业安装包，也不包含真实项目数据、密钥、日志、数据库、浏览器 Profile、LobsterAI 上游源码或 node_modules。

## 第一次使用

1. 将整个包复制到目标 Windows 电脑。
2. 按现有 PoC 文档准备 LobsterAI/OpenClaw runtime。
3. 在 PowerShell 中运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\tools\\verify-pack1.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\tools\\restore-agent-taxonomy.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\tools\\start-yuzhineng-portable.ps1
```

## 成果入口

任务完成后运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\tools\\open-projects-index.ps1
```

如果还没有项目成果，该脚本会提示先在 LobsterAI 里发起宇智能制造业获客任务。

## 安全边界

- 不读取或打包真实 API Key。
- 不包含运行数据库。
- 不包含浏览器 Cookie 或 Profile。
- 不包含真实客户项目数据。
- 所有外部动作保持 `draft_only` 或 `approval_required`。
- 不提供自动发布、自动评论、自动私信、自动邮件按钮。
"""


START_PORTABLE_PS1 = r'''$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $PSScriptRoot
$v2Root = Join-Path $packageRoot "openclaw-v2\v2"
$startScript = Join-Path $v2Root "scripts\start-yuzhineng.ps1"
$restoreScript = Join-Path $PSScriptRoot "restore-agent-taxonomy.ps1"

if (-not (Test-Path -LiteralPath $startScript)) {
  throw "找不到宇智能启动脚本：$startScript"
}

Write-Host "正在恢复宇智能标准 Agent..."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $restoreScript

Write-Host "正在启动宇智能桌面端..."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $startScript
'''


RESTORE_TAXONOMY_PS1 = r'''$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $PSScriptRoot
$v2Root = Join-Path $packageRoot "openclaw-v2\v2"
$repairScript = Join-Path $v2Root "scripts\repair_lobsterai_agent_taxonomy.ps1"
$outputDir = Join-Path $packageRoot "runtime-state"
$outputFile = Join-Path $outputDir "agent-taxonomy-repair.json"

if (-not (Test-Path -LiteralPath $repairScript)) {
  throw "找不到 Agent 修复脚本：$repairScript"
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $repairScript -OutputFile $outputFile

Write-Host "Agent taxonomy 恢复完成：$outputFile"
'''


OPEN_PROJECTS_INDEX_PS1 = r'''$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $PSScriptRoot
$v2Root = Join-Path $packageRoot "openclaw-v2\v2"
$projectsIndex = Join-Path $v2Root "projects\projects_index.html"

if (Test-Path -LiteralPath $projectsIndex) {
  Start-Process $projectsIndex
  Write-Host "已打开项目成果入口：$projectsIndex"
} else {
  Write-Host "当前包内还没有项目成果入口。请先在 LobsterAI 中运行一次宇智能制造业获客任务。"
  Write-Host "任务完成后，成果会生成在 v2\projects，并可通过 projects_index.html 查看。"
}
'''


VERIFY_PACK1_PS1 = r'''$ErrorActionPreference = "Stop"

$packageRoot = Split-Path -Parent $PSScriptRoot
$v2Root = Join-Path $packageRoot "openclaw-v2\v2"
$manifest = Join-Path $packageRoot "PACKAGE_MANIFEST.json"
$taxonomy = Join-Path $v2Root "config\agent_taxonomy.json"
$repair = Join-Path $v2Root "scripts\repair_lobsterai_agent_taxonomy.ps1"
$start = Join-Path $v2Root "scripts\start-yuzhineng.ps1"

$required = @($manifest, $taxonomy, $repair, $start)
foreach ($path in $required) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "PACK-1 校验失败，缺少文件：$path"
  }
}

$forbidden = @(
  "openclaw-v2\secrets",
  "openclaw-v2\logs",
  "openclaw-v2\database",
  "openclaw-v2\backups",
  "openclaw-v2\v2\data",
  "openclaw-v2\v2\projects",
  "openclaw-v2\v2\runtimes",
  "openclaw-v2\v2\client-shell\lobsterai\src",
  "openclaw-v2\v2\client-shell\lobsterai\src\node_modules"
)

foreach ($rel in $forbidden) {
  $path = Join-Path $packageRoot $rel
  if (Test-Path -LiteralPath $path) {
    throw "PACK-1 校验失败，包内出现禁止目录：$path"
  }
}

Write-Host "PACK-1 校验通过。"
Write-Host "下一步：运行 tools\restore-agent-taxonomy.ps1，然后运行 tools\start-yuzhineng-portable.ps1。"
'''


def build_package(output_root: Path = DEFAULT_OUTPUT, force: bool = False, dry_run: bool = False):
    output_root = Path(output_root)
    selected = [rel for rel in git_files() if is_allowed(rel)]
    rejected = [rel for rel in git_files() if not is_allowed(rel)]

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "output_root": str(output_root),
            "selected_count": len(selected),
            "rejected_count": len(rejected),
            "source_commit": current_commit(),
        }

    if output_root.exists():
        if not force:
            raise FileExistsError(f"Output already exists: {output_root}. Use --force to rebuild.")
        clean_output(output_root)

    package_root = output_root
    app_root = package_root / "openclaw-v2"
    app_root.mkdir(parents=True, exist_ok=True)

    copied = []
    for rel in selected:
        src = ROOT / rel
        if not src.is_file():
            continue
        dst = app_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    source_commit = current_commit()
    package_name = output_root.name

    write_text(package_root / "README_安装_CN.md", package_readme(package_name, source_commit))
    write_text(package_root / "tools" / "start-yuzhineng-portable.ps1", START_PORTABLE_PS1)
    write_text(package_root / "tools" / "restore-agent-taxonomy.ps1", RESTORE_TAXONOMY_PS1)
    write_text(package_root / "tools" / "open-projects-index.ps1", OPEN_PROJECTS_INDEX_PS1)
    write_text(package_root / "tools" / "verify-pack1.ps1", VERIFY_PACK1_PS1)

    manifest = {
        "package_name": package_name,
        "phase": "PACK-1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": source_commit,
        "package_root": str(package_root),
        "copied_files_count": len(copied),
        "included_capabilities": [
            "standard_agent_taxonomy",
            "growth_os_cleanroom_modules",
            "domestic_signal_growth_skill",
            "product_intelligence_skill",
            "manufacturing_multi_agent_workflow",
            "agent_taxonomy_restore_script",
            "project_index_open_helper",
        ],
        "excluded_runtime_data": [
            "secrets",
            "logs",
            "database",
            "backups",
            "v2/projects",
            "v2/data",
            "v2/runtimes",
            "lobsterai_upstream_source",
            "node_modules",
            "build_outputs",
        ],
        "external_action_mode": "draft_only_or_approval_required",
        "real_external_send_enabled": False,
        "copied_files": copied,
    }
    write_text(package_root / "PACKAGE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    safety = scan_package(package_root)
    result = {
        "ok": safety["ok"],
        "dry_run": False,
        "output_root": str(package_root),
        "source_commit": source_commit,
        "copied_files_count": len(copied),
        "safety": safety,
        "manifest": str(package_root / "PACKAGE_MANIFEST.json"),
        "readme": str(package_root / "README_安装_CN.md"),
    }
    write_text(package_root / "PACK1_BUILD_RESULT.json", json.dumps(result, ensure_ascii=False, indent=2))
    return result


def scan_package(package_root: Path):
    violations = []
    for path in package_root.rglob("*"):
        rel = _rel(path.relative_to(package_root))
        if path.is_dir():
            candidate = rel + "/"
        else:
            candidate = rel
        if is_forbidden(candidate):
            violations.append(rel)
    return {"ok": not violations, "violations": violations}


def main():
    parser = argparse.ArgumentParser(description="Create YuZhiNeng PACK-1 portable package PoC.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = build_package(Path(args.output), force=args.force, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
