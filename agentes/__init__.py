# -*- coding: utf-8 -*-
"""Os seis agentes do Instalador — Genial Labs AI.

Um arquivo por agente:

    destripador.py   1 · Destripador — lê o alvo inteiro, vira mapa estrutural
    professor.py     2 · Professor — transforma o mapa em 6 fases
    cetico.py        3 · Cético — objeta com evidência de arquivo:linha
    convicto.py      4 · Convicto — defende com evidência
    juiz.py          5 · Juiz — pontua objeções × defesas e decide
    socrates.py      6 · Sócrates — só pergunta; calibra pela sua nuance

Material nenhum vira ensino antes do tribunal (3 × 4 × 5). Sócrates não
trabalha sobre o material: trabalha sobre você.
"""
from .cetico import Cetico
from .convicto import Convicto
from .destripador import Destripador
from .juiz import Juiz
from .professor import Professor
from .socrates import Socrates, medir_nuance

__all__ = ["Destripador", "Professor", "Cetico", "Convicto", "Juiz",
           "Socrates", "medir_nuance"]
