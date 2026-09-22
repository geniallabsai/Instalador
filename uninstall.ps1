# Remove o wrapper e a pasta do instalador (Windows).
$ErrorActionPreference = "Continue"
$cmd = Join-Path $env:LOCALAPPDATA "GenialInstalador" "bin" "instalador.cmd"
if (Test-Path $cmd) { Remove-Item $cmd -Force; Write-Host "removido: $cmd" }
$dest = Join-Path $env:USERPROFILE ".genial-instalador"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force; Write-Host "removido: $dest" }
Write-Host "Genial Labs · INSTALADOR removido."
