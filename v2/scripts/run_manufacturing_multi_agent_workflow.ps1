param(
  [string]$InputFile = "",
  [string]$InputJson = "",
  [string]$Task = "",
  [string]$RunsRoot = "D:\OpenClaw\v2\data\workflow-runs",
  [string]$ProjectsRoot = "D:\OpenClaw\v2\projects",
  [string]$CreatedAt = "",
  [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$env:PYTHONIOENCODING = "utf-8"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonFile = Join-Path $scriptDir "run_manufacturing_multi_agent_workflow.py"

$python = Get-Command python -ErrorAction SilentlyContinue
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $python -and -not $py) {
  throw "Python runtime not found. Please install Python under D:\DevTools or make python/py available for this session."
}

$argsList = @($pythonFile, "--runs-root", $RunsRoot, "--projects-root", $ProjectsRoot)
if ($InputFile.Trim().Length -gt 0) {
  $argsList += @("--input-file", $InputFile)
} elseif ($InputJson.Trim().Length -gt 0) {
  $argsList += @("--input-json", $InputJson)
} elseif ($Task.Trim().Length -gt 0) {
  $argsList += @("--task", $Task)
}
if ($CreatedAt.Trim().Length -gt 0) {
  $argsList += @("--created-at", $CreatedAt)
}
if ($OutputFile.Trim().Length -gt 0) {
  $argsList += @("--output-file", $OutputFile)
}

if ($python) {
  & $python.Source @argsList
} else {
  & $py.Source -3 @argsList
}
exit $LASTEXITCODE
