param(
  [string]$DbPath = "$env:APPDATA\LobsterAI\lobsterai.sqlite",
  [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$script = "D:\OpenClaw\v2\scripts\repair_lobsterai_agent_taxonomy.py"
$argsList = @($script, "--db-path", $DbPath)
if ($OutputFile.Trim().Length -gt 0) {
  $argsList += @("--output-file", $OutputFile)
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  & $python.Source @argsList
} else {
  & py -3 @argsList
}
exit $LASTEXITCODE
