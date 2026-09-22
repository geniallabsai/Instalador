# -*- coding: utf-8 -*-
"""Juiz — agente 5 de 6.

Arbitra Cético × Convicto com aritmética aberta: pena = soma dos pesos das
objeções (crítico 8, alto 5, médio 2, baixo 1), ganho = min(10, 2×defesas),
confiança = clamp(90 − pena + ganho, 5, 99). ≥80 sólido, ≥55 com ressalvas,
abaixo disso questionado. O veredito volta com a pontuação completa.
"""

import json

from instalador_core import llm
from .comum import _fatos


NIVEL_PENTO = {"critico": 8, "alto": 5, "medio": 2, "baixo": 1}


class Juiz:
    nome = "Juiz"
    papel = "arbitra Cético × Convicto: pontua, mede a confiança e redige o veredito"

    def decidir(self, mapa, objecoes, defesas):
        pena = sum(NIVEL_PENTO.get(o.get("nivel", "baixo"), 1) for o in objecoes)
        ganho = min(10, 2 * len(defesas))
        confianca = max(5, min(99, 90 - pena + ganho))
        if confianca >= 80:
            decisao = "material sólido — explicar como está, citando as ressalvas"
        elif confianca >= 55:
            decisao = "aceito com ressalvas — ensinar primeiro as objeções marcadas, depois o mérito"
        else:
            decisao = "questionado — o aluno precisa ver onde quebra ANTES de aprender o caminho feliz"
        cheio = int(round(confianca / 5.0))
        barra = "█" * cheio + "░" * (20 - cheio)
        resumo = ("O Cético apresentou %d objeções (pena %d); o Convicto sustentou %d defesas (ganho %d). "
                  "Confiança final: %d/100. Veredito: %s.") % (
                      len(objecoes), pena, len(defesas), ganho, confianca, decisao)
        return {"confianca": confianca, "decisao": decisao, "barra": barra,
                "pontuacao": {"pena": pena, "ganho": ganho}, "resumo": resumo,
                "objecoes": objecoes, "defesas": defesas}
