param(
  [string]$InputJson = "",
  [string]$InputFile = "",
  [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
$env:PYTHONIOENCODING = "utf-8"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonFile = Join-Path $scriptDir "domestic_signal_growth.py"

$python = Get-Command python -ErrorAction SilentlyContinue
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $python -and -not $py) {
  throw "Python runtime not found. Please install Python under D:\DevTools or make python/py available for this session."
}

$argsList = @($pythonFile)
if ($InputFile.Trim().Length -gt 0) {
  $argsList += @("--input-file", $InputFile)
} elseif ($InputJson.Trim().Length -gt 0) {
  $argsList += @("--input-json", $InputJson)
}
if ($OutputFile.Trim().Length -gt 0) {
  $argsList += @("--output-file", $OutputFile)
}

if ($python) {
  & $python.Source @argsList
} else {
  & $py.Source -3 @argsList
}
