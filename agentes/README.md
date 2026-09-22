# Agentes

Seis agentes. **Um arquivo por agente.** Material nenhum vira ensino antes
do tribunal; argumento nenhum vale sem evidência (`arquivo:linha`).

| Arquivo | Agente | Papel |
|---|---|---|
| `destripador.py` | **Destripador** | lê o alvo inteiro: arquivos, símbolos, imports, riscos, pontos fortes → mapa estrutural |
| `professor.py` | **Professor** | transforma o mapa + veredito em 6 fases didáticas (complexo entra, simples sai) |
| `cetico.py` | **Cético** | objeta cada ponto com evidência de arquivo:linha |
| `convicto.py` | **Convicto** | defende a explicação mais forte, também com evidência |
| `juiz.py` | **Juiz** | pena × ganho → confiança 5–99 → veredito |
| `socrates.py` | **Sócrates** | mede sua nuance (jargão, hesitação, extensão) e recalibra cada pergunta — nunca responde |
| `comum.py` | — | o retrato `_fatos` que os debatedores mostram ao modelo de IA |

## Rodar o tribunal isoladamente

```python
import sys
sys.path.insert(0, "/caminho/para/Instalador")
from instalador_core import destripador
from agentes import Cetico, Convicto, Juiz, Professor

mapa     = destripador.Destripador().destruir("caminho/qualquer/coisa")
objecoes = Cetico().objetar(mapa)
defesas  = Convicto().defender(mapa)
juizo    = Juiz().decidir(mapa, objecoes, defesas)
curso    = Professor().ensinar(mapa, juizo)
print(juizo["confianca"], juizo["decisao"])
```

O detalhe completo da matemática e do método está em [`../AGENTES.md`](../AGENTES.md).
