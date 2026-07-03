param(
  [string]$InputFile = "",
  [string]$InputJson = "",
  [string]$Task = "",
  [string]$OutputFile = "",
  [bool]$MirrorLobsterAIUI = $true
)

$ErrorActionPreference = "Stop"
$ScriptPath = "D:\OpenClaw\v2\scripts\run_manufacturing_multi_agent_workflow.ps1"

$argsList = @()
if ($InputFile.Trim().Length -gt 0) {
  $argsList += @("-InputFile", $InputFile)
} elseif ($InputJson.Trim().Length -gt 0) {
  $argsList += @("-InputJson", $InputJson)
} elseif ($Task.Trim().Length -gt 0) {
  $argsList += @("-Task", $Task)
}
if ($OutputFile.Trim().Length -gt 0) {
  $argsList += @("-OutputFile", $OutputFile)
}
$argsList += @("-MirrorLobsterAIUI", $MirrorLobsterAIUI)

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @argsList
exit $LASTEXITCODE
