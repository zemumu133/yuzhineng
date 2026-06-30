param(
  [string]$Root = "D:\OpenClaw"
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

Write-Host "=== v2 task precheck ==="
$git = Resolve-Git
if (-not $git) {
  Write-Host "Git: missing"
  exit 1
}

Write-Host "Git: $git"
Write-Host "Branch:"
& $git -C $Root branch --show-current

Write-Host "Git status:"
& $git -C $Root status --short --branch

Write-Host "Required files:"
$required = @(
  "AGENTS.md",
  "v2\CODEX_WORKFLOW_CN.md",
  "v2\PHASE_GATE_CHECKLIST_CN.md",
  "v2\V2_FINAL_GOAL_CN.md",
  ".codex\agents"
)
foreach ($item in $required) {
  $path = Join-Path $Root $item
  if (Test-Path -LiteralPath $path) {
    Write-Host "[OK] $item"
  } else {
    Write-Host "[MISSING] $item"
  }
}

Write-Host "Tracked sensitive/runtime/build risk:"
$risk = Test-TrackedRisk -GitExe $git -RepoRoot $Root
if ($risk) {
  $risk | ForEach-Object { Write-Host "[RISK] $_" }
  exit 2
}
Write-Host "[OK] no tracked sensitive/runtime/build files"
Write-Host "Precheck finished."

