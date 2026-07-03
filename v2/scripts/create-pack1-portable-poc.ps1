param(
  [string]$Output = "D:\OpenClaw\v2\packages\yuzhineng-pack1-portable-poc",
  [switch]$Force,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$script = "D:\OpenClaw\v2\scripts\create-pack1-portable-poc.py"

if (-not (Test-Path -LiteralPath $script)) {
  throw "Cannot find PACK-1 builder: $script"
}

$argsList = @($script, "--output", $Output)
if ($Force) {
  $argsList += "--force"
}
if ($DryRun) {
  $argsList += "--dry-run"
}

python @argsList
