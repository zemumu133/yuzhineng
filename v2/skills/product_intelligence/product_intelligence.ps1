param(
  [string]$InputFile = "",
  [string]$InputJson = "",
  [string]$OutputFile = "",
  [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "product_intelligence.py"

$ArgsList = @()
if ($InputFile) {
  $ArgsList += @("--input-file", $InputFile)
}
if ($InputJson) {
  $ArgsList += @("--input-json", $InputJson)
}
if ($OutputFile) {
  $ArgsList += @("--output-file", $OutputFile)
}
if ($OutputDir) {
  $ArgsList += @("--output-dir", $OutputDir)
}

python $PythonScript @ArgsList
exit $LASTEXITCODE
