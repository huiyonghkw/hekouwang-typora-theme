<#
hekouwang · Windows installer (free V2)

Usage (PowerShell):
  .\scripts\install-windows.ps1

Copies only the free pair and bundled Inter fonts. Existing theme CSS is
backed up below the themes folder, where Typora will not list it as a theme.
#>
[CmdletBinding()]
param([string]$ThemeDir = (Join-Path $env:APPDATA 'Typora\themes'))

$ErrorActionPreference = 'Stop'
$slug = 'hekouwang'
$root = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupDir = Join-Path $ThemeDir ".${slug}-backups"
$variants = @($slug, "${slug}-dark")
$legacy = @("${slug}-claude", "${slug}-claude-dark")

function Write-Ok([string]$Message) { Write-Host "  ✓ $Message" -ForegroundColor Green }
function Write-Warn([string]$Message) { Write-Host "  ! $Message" -ForegroundColor Yellow }

Write-Host 'hekouwang · install (free · V2 · Windows)'
Write-Host '────────────────────────────────────────'
if (-not (Test-Path -LiteralPath $ThemeDir -PathType Container)) {
  throw "Typora themes folder not found: $ThemeDir`nInstall Typora first, then use Preferences → Appearance → Open Theme Folder."
}
foreach ($variant in $variants) {
  $source = Join-Path $root "theme\$variant.css"
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing $source. Run: python scripts\build.py --tier free" }
}
foreach ($variant in ($variants + $legacy)) {
  $current = Join-Path $ThemeDir "$variant.css"
  if (Test-Path -LiteralPath $current -PathType Leaf) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Copy-Item -LiteralPath $current -Destination (Join-Path $backupDir "$variant-$stamp.css") -Force
    Write-Ok "backed up $variant.css"
  }
}
foreach ($variant in $variants) {
  Copy-Item -LiteralPath (Join-Path $root "theme\$variant.css") -Destination (Join-Path $ThemeDir "$variant.css") -Force
  Write-Ok "installed $variant.css"
}
foreach ($variant in $legacy) {
  $current = Join-Path $ThemeDir "$variant.css"
  if (Test-Path -LiteralPath $current -PathType Leaf) { Remove-Item -LiteralPath $current -Force; Write-Ok "removed legacy $variant.css" }
}
$fontSource = Join-Path $root "theme\$slug\fonts"
$fontTarget = Join-Path $ThemeDir "$slug\fonts"
if (Test-Path -LiteralPath $fontSource -PathType Container) {
  New-Item -ItemType Directory -Force -Path $fontTarget | Out-Null
  $fonts = Get-ChildItem -LiteralPath $fontSource -File
  foreach ($font in $fonts) { Copy-Item -LiteralPath $font.FullName -Destination $fontTarget -Force }
  Write-Ok "installed $($fonts.Count) bundled Inter font file(s)"
} else { Write-Warn 'bundled fonts folder not found; Latin text will fall back to the system font' }
Write-Host '────────────────────────────────────────'
Write-Host 'Done. Quit Typora completely, reopen it, then select:'
Write-Host '  • Hekouwang / Hekouwang Dark'
Write-Host 'Changing a theme does not reload a modified CSS file; restart Typora after updates.'
