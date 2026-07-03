param(
  [Parameter(Mandatory=$true)]
  [string]$TaskOutputDir,
  [string]$ProjectsRoot = "D:\OpenClaw\v2\projects",
  [string]$ProjectSlug = "",
  [string]$ProjectName = "",
  [string]$CreatedAt = "",
  [string]$ReportSource = "",
  [string]$HandoffSource = ""
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$env:PYTHONIOENCODING = "utf-8"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonFile = Join-Path $scriptDir "archive_manufacturing_growth_result.py"
$python = Get-Command python -ErrorAction SilentlyContinue
$py = Get-Command py -ErrorAction SilentlyContinue

if (-not $python -and -not $py) {
  throw "Python runtime not found. Please make python/py available for this session."
}

$argsList = @(
  $pythonFile,
  "--task-output-dir", $TaskOutputDir,
  "--projects-root", $ProjectsRoot
)

if ($ProjectSlug.Trim().Length -gt 0) { $argsList += @("--project-slug", $ProjectSlug) }
if ($ProjectName.Trim().Length -gt 0) { $argsList += @("--project-name", $ProjectName) }
if ($CreatedAt.Trim().Length -gt 0) { $argsList += @("--created-at", $CreatedAt) }
if ($ReportSource.Trim().Length -gt 0) { $argsList += @("--report-source", $ReportSource) }
if ($HandoffSource.Trim().Length -gt 0) { $argsList += @("--handoff-source", $HandoffSource) }

if ($python) {
  & $python.Source @argsList
} else {
  & $py.Source -3 @argsList
}
