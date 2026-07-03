param(
  [string]$Root = "D:\OpenClaw",
  [string]$ReportPath = "D:\OpenClaw\v2\reports\PHASE_R0_5_CODEX_GOVERNANCE_REPORT_CN.md"
)

$ErrorActionPreference = "Continue"

function Resolve-Git {
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $portable = "D:\DevTools\Git\cmd\git.exe"
  if (Test-Path -LiteralPath $portable) { return $portable }
  return $null
}

function Test-TrackedRisk {
  param([string]$GitExe, [string]$RepoRoot)
  $tracked = & $GitExe -C $RepoRoot ls-files 2>$null
  $tracked | Where-Object {
    $_ -match '(^|/)(secrets|logs|backups|node_modules|dist|build|cache)(/|$)' -or
    $_ -match '(^|/).*\.(env|key|token|pem|p12|pfx|sqlite|log|zip|7z|rar|tmp)$' -or
    $_ -match 'Default/(Cookies|Network|Local Storage|Session Storage)'
  }
}

Write-Host "=== v2 task postcheck ==="
$git = Resolve-Git
if (-not $git) {
  Write-Host "Git: missing"
  exit 1
}

Write-Host "Git: $git"
Write-Host "Git status:"
& $git -C $Root status --short --branch

Write-Host "Tracked sensitive/runtime/build risk:"
$risk = Test-TrackedRisk -GitExe $git -RepoRoot $Root
if ($risk) {
  $risk | ForEach-Object { Write-Host "[RISK] $_" }
  exit 2
}
Write-Host "[OK] no tracked sensitive/runtime/build files"

Write-Host "Report check:"
if (Test-Path -LiteralPath $ReportPath) {
  Write-Host "[OK] report exists: $ReportPath"
} else {
  Write-Host "[MISSING] report: $ReportPath"
}

Write-Host "Phase gate check:"
$gate = Join-Path $Root "v2\PHASE_GATE_CHECKLIST_CN.md"
if (Test-Path -LiteralPath $gate) {
  Write-Host "[OK] phase gate checklist exists"
} else {
  Write-Host "[MISSING] phase gate checklist"
}

Write-Host "Postcheck finished."

