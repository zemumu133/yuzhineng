param(
  [string]$InputJson = "",
  [string]$InputFile = "",
  [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$entry = Join-Path $scriptDir "domestic_signal_growth.ps1"

& $entry -InputJson $InputJson -InputFile $InputFile -OutputFile $OutputFile
