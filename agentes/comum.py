# -*- coding: utf-8 -*-
"""
comum — material compartilhado dos debatedores.

O retrato `_fatos` é o único pedaço do mapa que Cético, Convicto e Juiz
enxergam em prosa ao pedir ajuda ao modelo de IA: resumo, linguagens,
top de arquivos, riscos e pontos fortes, cortado para caber num prompt.
Os debatedores não leem disco; leem esse retrato.
"""

import json


def _fatos(mapa, limite=1800):
    trecho = {
        "nome": mapa.get("nome"),
        "resumo": (mapa.get("resumo") or "")[:240],
        "linguagens": mapa.get("linguagens"),
        "arquivos_total": mapa.get("arquivos_total"),
        "linhas_total": mapa.get("linhas_total"),
        "top": [a["caminho"] for a in sorted(mapa.get("arquivos", []), key=lambda x: -x["linhas"])[:10]],
        "riscos": mapa.get("riscos", [])[:6],
        "fortes": [f["titulo"] for f in mapa.get("fortes", [])],
    }
    return json.dumps(trecho, ensure_ascii=False)[:limite]
