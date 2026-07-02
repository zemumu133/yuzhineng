param(
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$appRoot = "D:\OpenClaw\v2\client-shell\lobsterai\src"
$gitPath = "D:\DevTools\Git\cmd"
$portableGitRoot = "D:\DevTools\PortableGit"
$openClawSource = "D:\OpenClaw\v2\runtimes\lobsterai-openclaw-src"
$shimPath = "D:\OpenClaw\v2\runtimes\shims"

if (-not (Test-Path -LiteralPath (Join-Path $appRoot "package.json"))) {
  throw "YuZhiNeng launcher cannot find LobsterAI source at $appRoot"
}

if (Test-Path -LiteralPath $gitPath) {
  $env:PATH = "$gitPath;$env:PATH"
}

if (Test-Path -LiteralPath $portableGitRoot) {
  $env:PATH = "$portableGitRoot\cmd;$portableGitRoot\bin;$portableGitRoot\usr\bin;$env:PATH"
}

if (Test-Path -LiteralPath $shimPath) {
  $env:PATH = "$shimPath;$env:PATH"
}

if (Test-Path -LiteralPath $openClawSource) {
  $env:OPENCLAW_SRC = $openClawSource
}

$env:npm_config_registry = "https://registry.npmmirror.com"
$env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
$env:ELECTRON_BUILDER_BINARIES_MIRROR = "https://npmmirror.com/mirrors/electron-builder-binaries/"

Set-Location -LiteralPath $appRoot

Write-Host "Starting YuZhiNeng desktop shell..."
Write-Host "App root: $appRoot"
Write-Host "Mode: LobsterAI UI + embedded OpenClaw runtime"

npm run electron:dev:openclaw

if (-not $NoPause) {
  Write-Host ""
  Write-Host "YuZhiNeng process ended. Press Enter to close this window."
  [void][System.Console]::ReadLine()
}
