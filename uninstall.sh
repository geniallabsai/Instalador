#!/usr/bin/env bash
# Remove o comando global e a pasta do instalador. O seu código não é tocado.
set -u
rm -f "$HOME/.local/bin/instalador" && echo "removido: ~/.local/bin/instalador"
rm -rf "$HOME/.genial-instalador" && echo "removido: ~/.genial-instalador"
echo "Genial Labs · INSTALADOR removido. As saídas geradas (pasta ./saida) continuam onde estão."
