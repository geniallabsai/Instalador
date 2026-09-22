# -*- coding: utf-8 -*-
"""
Convicto — agente 4 de 6.

Defende o material com a versão mais forte da explicação, sempre
apontando evidência (arquivo:linha ou artefato — teste, CI,
Dockerfile, LICENSE, README, docstrings, type hints, superfície
pequena). Sem defesa nenhuma, a última âncora é o próprio mapa.
"""

import json

from instalador_core import llm
from .comum import _fatos


class Convicto:
    nome = "Convicto"
    papel = "defende o material com a versão mais forte da explicação, sempre apontando evidência"

    def defender(self, mapa):
        defesas = []
        for f in mapa.get("fortes", []):
            t = f["titulo"]
            onde = f.get("onde", "projeto")
            if t == "teste":
                defesas.append({"texto": "existe teste no projeto — regressão tem rede de proteção", "evidencia": onde})
            elif t == "ci":
                defesas.append({"texto": "pipeline de CI ativo: nada entra sem passar pelos gates", "evidencia": onde})
            elif t == "dockerfile":
                defesas.append({"texto": "Dockerfile presente: ambiente reproduzível, fim do 'mas na minha máquina...'", "evidencia": onde})
            elif t == "license":
                defesas.append({"texto": "licença publicada: uso e derivação têm regra", "evidencia": onde})
            elif t == "readme":
                defesas.append({"texto": "README explica o propósito: o projeto nasce documentado", "evidencia": onde})
            elif t == "docstrings":
                defesas.append({"texto": "%.0f%% das funções documentam o próprio contrato" % f.get("extra", 0), "evidencia": onde})
            elif t == "type_hints":
                defesas.append({"texto": "type hints presentes: o contrato fala dentro do código", "evidencia": onde})
            elif t == "pequeno":
                defesas.append({"texto": "superfície pequena: %d arquivos — dá para ler tudo antes de confiar" % f.get("extra", 0),
                                "evidencia": onde})
        if not defesas:
            defesas.append({"texto": "o mapa estrutural existe e é verificável arquivo a arquivo — cada afirmação deste curso aponta para o código",
                            "evidencia": "mapa.json"})
        txt = llm.chamar(
            "Você é o Convicto do Genial Labs: sustenta o material com a versão mais forte da explicação, "
            "sempre com evidência. Responda SOMENTE com até 3 linhas iniciadas por '- '.",
            _fatos(mapa))
        if txt:
            linhas = [l.strip().lstrip("-• ").strip() for l in txt.splitlines()]
            linhas = [l for l in linhas if l][:3]
            defesas.extend({"texto": l, "evidencia": "modelo"} for l in linhas)
        return defesas[:8]
