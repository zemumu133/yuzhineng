param(
  [switch]$InitLocalConfig,
  [switch]$Run,
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

Write-Host "Usage:"
Write-Host "  .\dev-autorun-gate.ps1 -InitLocalConfig"
Write-Host "  .\dev-autorun-gate.ps1 -Run"
