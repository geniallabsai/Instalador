#!/usr/bin/env bash
# Genial Labs · INSTALADOR — instalação em 1 comando (Linux/macOS/WSL/Git Bash).
# Clona o repositório para ~/.genial-instalador e cria o wrapper ~/.local/bin/instalador.
set -euo pipefail

REPO_ZIP="https://codeload.github.com/geniallabsai/Instalador/zip/refs/heads/main"
REPO_GIT="https://github.com/geniallabsai/Instalador.git"
DEST="$HOME/.genial-instalador"
BIN="$HOME/.local/bin"
NOME_INSTALADO="genial-instalador"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Genial Labs · INSTALADOR                            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "[1/4] verificando pré-requisitos…"
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "  python3 não encontrado no PATH. Instale Python 3.7+ e rode de novo." >&2
  exit 1
fi
echo "  $PY ok"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if [ -d "$DEST" ]; then
  echo "[2/4] repositório já em $DEST — atualizando…"; rm -rf "$DEST"
else
  echo "[2/4] baixando o Instalador…"
fi
if git clone --depth 1 "$REPO_GIT" "$DEST" >/dev/null 2>&1; then
  echo "  clone git ok"
else
  curl -fsSL "$REPO_ZIP" -o "$TMP/inst.zip" && unzip -q "$TMP/inst.zip" -d "$TMP"
  mv "$TMP"/Instalador-* "$DEST" || cp -r "$TMP"/Instalador-* "$DEST"
  echo "  zip codeload ok (git indisponível?)"
fi
# normaliza quebras de linha (zip pode trazer CRLF)
find "$DEST" -type f \( -name "*.py" -o -name "*.sh" -o -name "instalador" \) -exec sed -i 's/\r$//' {} +

echo "[3/4] criando o comando global…"
mkdir -p "$BIN"
cat > "$BIN/instalador" <<'WRAPPER'
#!/bin/sh
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo 'instalador: python3 nao encontrado' >&2; exit 127; }
exec "$PY" "$HOME/.genial-instalador/instalador" "$@"
WRAPPER
chmod +x "$BIN/instalador"

echo "[4/4] auto-teste…"
if "$BIN/instalador" status >/dev/null 2>&1; then
  echo ""
  echo "✓ Genial Labs · INSTALADOR instalado."
  echo ""
  echo "  próximos passos:"
  echo "    instalador                ← banner + menu"
  echo "    instalador curso .        ← este diretório inteiro vira curso (PDF+DOCX+Obsidian)"
  echo "    instalador chat . --fase 3"
  echo "    instalador debate "seu tema""
  case ":$PATH:" in
    *":$BIN:"*) ;;
    *) echo ""
         echo "  avise: adicione $BIN ao PATH  →  export PATH="$BIN:\\$PATH"" ;;
  esac
else
  echo "auto-teste falhou — rode manualmente: $BIN/instalador status" >&2
  exit 1
fi
