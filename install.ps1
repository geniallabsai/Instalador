# Genial Labs · INSTALADOR — instalação Windows nativo (PowerShell 5.1+).
# Baixa o repositório, coloca em %USERPROFILE%\.genial-instalador e cria
# o wrapper em %LOCALAPPDATA%\GenialInstalador\bin (adicionado ao PATH de usuário).
$ErrorActionPreference = "Stop"
Write-Host "Genial Labs · INSTALADOR — instalação Windows" -ForegroundColor Cyan
Write-Host ""

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw "python não encontrado no PATH. Instale em python.org marcando 'Add python.exe to PATH'." }
Write-Host "python ok: $($py.Source)"

$tmp = Join-Path $env:TEMP ("gl-instalador-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory $tmp | Out-Null
try {
  Write-Host "[1/4] baixando o Instalador…" -ForegroundColor DarkGray
  $zip = Join-Path $tmp "pacote.zip"
  Invoke-WebRequest -Uri "https://codeload.github.com/geniallabsai/Instalador/zip/refs/heads/main" -OutFile $zip -UseBasicParsing
  $ext = Join-Path $tmp "x"
  Expand-Archive -Path $zip -DestinationPath $ext
  $origem = Get-ChildItem $ext | Select-Object -First 1
  $dest = Join-Path $env:USERPROFILE ".genial-instalador"
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  Copy-Item $origem.FullName $dest -Recurse
  Write-Host "[2/4] instalado em $dest" -ForegroundColor DarkGray
  $bin = Join-Path $env:LOCALAPPDATA "GenialInstalador" "bin"
  New-Item -ItemType Directory $bin -Force | Out-Null
  $cmd = Join-Path $bin "instalador.cmd"
  Set-Content -Path $cmd -Encoding ASCII -Value (@(
    "@echo off",
    "set PYTHONUTF8=1",
    (""{0}" "{1}\instalador" %*" -f $py.Source, $dest)
  ) -join "`r`n")
  Write-Host "[3/4] wrapper em $cmd" -ForegroundColor DarkGray
  $pathUser = [Environment]::GetEnvironmentVariable("Path", "User")
  if ($pathUser -notlike "*$bin*") {
    [Environment]::SetEnvironmentVariable("Path", "$pathUser;$bin", "User")
    Write-Host "[4/4] PATH de usuário atualizado — abra um NOVO terminal para o comando valer." -ForegroundColor Yellow
  } else {
    Write-Host "[4/4] PATH já contém o bin — pronto." -ForegroundColor Green
  }
  & $cmd "status" *> $null
  if ($LASTEXITCODE -ne 0) { throw "auto-teste falhou: $cmd status" }
  Write-Host ""
  Write-Host "✓ Genial Labs · INSTALADOR instalado." -ForegroundColor Green
  Write-Host ""
  Write-Host "  próximos passos (terminal novo):" -ForegroundColor Cyan
  Write-Host "    instalador                 ← banner + menu"
  Write-Host "    instalador curso .         ← este diretório vira curso completo"
  Write-Host "    instalador chat . --fase 3"
} finally {
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
