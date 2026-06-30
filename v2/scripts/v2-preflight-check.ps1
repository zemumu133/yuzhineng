param(
  [string]$Root = "D:\OpenClaw"
)

$ErrorActionPreference = "Continue"

function Test-Tool {
  param([string]$Name)
  try {
    $cmd = Get-Command $Name -ErrorAction Stop
    $version = & $Name --version 2>&1 | Select-Object -First 1
    [pscustomobject]@{
      Tool = $Name
      Status = "OK"
      Path = $cmd.Source
      Version = ($version -join " ")
    }
  } catch {
    [pscustomobject]@{
      Tool = $Name
      Status = "MISSING"
      Path = ""
      Version = $_.Exception.Message
    }
  }
}

function Test-PathSafe {
  param([string]$Path, [string]$Name)
  [pscustomobject]@{
    Name = $Name
    Path = $Path
    Status = if (Test-Path -LiteralPath $Path) { "EXISTS" } else { "MISSING" }
  }
}

Write-Host "=== V2 Preflight Check ==="
Write-Host "Root: $Root"
Write-Host ""

Write-Host "[Tools]"
@("git", "node", "npm", "pnpm", "python", "docker") | ForEach-Object { Test-Tool $_ } | Format-Table -AutoSize

Write-Host ""
Write-Host "[Key Paths]"
@(
  @{Name="v2 workspace"; Path=Join-Path $Root "v2"},
  @{Name="secrets dir"; Path=Join-Path $Root "secrets"},
  @{Name="logs dir"; Path=Join-Path $Root "logs"},
  @{Name="database dir"; Path=Join-Path $Root "database"},
  @{Name="backups dir"; Path=Join-Path $Root "backups"}
) | ForEach-Object { Test-PathSafe -Name $_.Name -Path $_.Path } | Format-Table -AutoSize

Write-Host ""
Write-Host "[Git]"
try {
  $gitRoot = git -C $Root rev-parse --show-toplevel 2>$null
  $branch = git -C $Root branch --show-current 2>$null
  Write-Host "Git root: $gitRoot"
  Write-Host "Current branch: $branch"
  $trackedRisk = git -C $Root ls-files 2>$null | Where-Object {
    $_ -match '(^|/)(secrets|logs|backups|node_modules|dist|build|cache)(/|$)' -or
    $_ -match '(^|/).*\.(env|key|pem|p12|pfx)$'
  }
  if ($trackedRisk) {
    Write-Host "Risk paths tracked by Git (path only, content not read):"
    $trackedRisk | ForEach-Object { Write-Host "- $_" }
  } else {
    Write-Host "No tracked high-risk paths found."
  }
} catch {
  Write-Host "Git is unavailable or this root is not a Git repository."
}

Write-Host ""
Write-Host "Preflight finished."
