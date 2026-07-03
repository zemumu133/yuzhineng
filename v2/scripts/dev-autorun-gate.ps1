param(
  [switch]$InitLocalConfig,
  [switch]$Run,
  [switch]$RunPhase2E,
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "dev-autorun-gate.py"

if ($InitLocalConfig) {
  & $Python $scriptPath --init-local-config
  exit $LASTEXITCODE
}

if ($Run) {
  $env:YUZHINENG_DEV_AUTO_RUN = "1"
  & $Python $scriptPath --run
  exit $LASTEXITCODE
}

if ($RunPhase2E) {
  $env:YUZHINENG_DEV_AUTO_RUN = "1"
  & $Python $scriptPath --run-phase2e
  exit $LASTEXITCODE
}

Write-Host "Usage:"
Write-Host "  .\dev-autorun-gate.ps1 -InitLocalConfig"
Write-Host "  .\dev-autorun-gate.ps1 -Run"
Write-Host "  .\dev-autorun-gate.ps1 -RunPhase2E"
