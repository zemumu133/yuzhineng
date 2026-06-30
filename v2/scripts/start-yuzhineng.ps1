param(
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$appRoot = "D:\OpenClaw\v2\client-shell\lobsterai\src"
$gitPath = "D:\DevTools\Git\cmd"

if (-not (Test-Path -LiteralPath (Join-Path $appRoot "package.json"))) {
  throw "YuZhiNeng launcher cannot find LobsterAI source at $appRoot"
}

if (Test-Path -LiteralPath $gitPath) {
  $env:PATH = "$gitPath;$env:PATH"
}

$env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
$env:ELECTRON_BUILDER_BINARIES_MIRROR = "https://npmmirror.com/mirrors/electron-builder-binaries/"

Set-Location -LiteralPath $appRoot

Write-Host "Starting YuZhiNeng desktop shell..."
Write-Host "App root: $appRoot"
Write-Host "Note: Phase 1A currently starts LobsterAI UI. OpenClaw runtime repair is the next step."

npm run electron:dev

if (-not $NoPause) {
  Write-Host ""
  Write-Host "YuZhiNeng process ended. Press Enter to close this window."
  [void][System.Console]::ReadLine()
}
