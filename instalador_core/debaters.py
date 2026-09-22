# -*- coding: utf-8 -*-
"""Compatibilidade: os três debatedores agora moram em ``agentes/cetico.py``,
``agentes/convicto.py`` e ``agentes/juiz.py``."""
from agentes.comum import _fatos                  # noqa: F401
from agentes.cetico import Cetico                 # noqa: F401
from agentes.convicto import Convicto             # noqa: F401
from agentes.juiz import Juiz, NIVEL_PENTO        # noqa: F401
