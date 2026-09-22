██████╗   ███████╗  ███╗   ███╗  ███╗   █████╗   ██╗        ██╗        █████╗   ██████╗   ███████╗
██╔══██╗  ██╔════╝  ████╗ ████║  ████╗  ██╔══██╗  ██║        ██║       ██╔══██╗  ██╔══██╗  ██╔════╝
██████╔╝  █████╗    ██╔████╔██║  ██╔██║  ███████║  ██║        ██║       ███████║  ██████╔╝  █████╗  
██╔══██╗  ██╔══╝    ██║╚██╔╝██║  ██║╚██║  ██╔══██║  ██║        ██║       ██╔══██║  ██╔═══██╗  ╚════╝  
██║  ██║  ███████╗  ██║ ╚═╝ ██║  ██║ ╚██║  ██║  ██║  ███████╗   ███████╗  ██║  ██║  ██║   ██║  ███████╗
╚═╝  ╚═╝  ╚══════╝  ╚═╝     ╚═╝  ╚═╝  ╚═╝  ╚═╝  ╚═╝  ╚══════╝   ╚══════╝  ╚═╝  ╚═╝  ╚═╝   ╚═╝  ╚══════╝

# Instalador

> O instalador da Genial Labs AI. **Destrincha qualquer código, programa ou pasta — e transforma em curso.**

Ele não resume. Ele destrincha: abre o material por dentro, mapeia quem fala com quem,
caça risco com evidência (arquivo:linha), passa o resultado por um tribunal de agentes
e só então escreve o ensino. Saída garantida em todo comando de curso:
**PDF**, **DOCX**, markdown legível por outros agentes, JSON estrutural,
diagramas **mermaid** e um vault **Obsidian**.

## Instalação

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/geniallabsai/Instalador/main/install.sh | bash
instalador
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/geniallabsai/Instalador/main/install.ps1 | iex
instalador
```

### Manual

```bash
git clone https://github.com/geniallabsai/Instalador.git
cd Instalador
bash install.sh                      # Linux/macOS
powershell -ExecutionPolicy Bypass -File install.ps1   # Windows
```

O instalador copia o pacote para `~/.genial-labs/instalador` e cria o wrapper
`instalador` em `~/.local/bin`, chamando `python3` explicitamente — sem mágica de
PATH, funciona inclusive no Git Bash. Desinstala com `bash uninstall.sh` (ou
`uninstall.ps1` no Windows).

**Requisito único:** Python 3.7+. Zero pacote de pip.

## Primeiro comando

```bash
instalador curso exemplos/calculadora
```

O terminal narra o ritual enquanto ele acontece:

```
Destripador › lendo arquivos 8/8
Destripador › conectando dependências e caçando riscos
Cético › caçando objeções com evidência…
Convicto › reunindo defesas…
Juiz › ponderando…
Juiz › confiança 59/100 · ████████████░░░░░░░░
Professor › escrito 6/6: Prática

SAÍDA: saida/<alvo>-<timestamp>/
  curso.pdf · curso.docx · curso.md · mapa.json · mapa.mmd · curso.mmd · obsidian/
```

A calculadora de exemplo tem falhas **plantadas** de propósito — credenciais
`ghp_` e `AKIA` em claro, `eval`, `shell=True` — e o tribunal descobre todas.

## Comandos

| Comando | O que faz |
|---|---|
| `instalador` | banner + menu |
| `instalador destri ALVO` | só o mapa estrutural (`mapa.json`, `mapa.mmd`) |
| `instalador curso ALVO` | pipeline completo → os 7 artefatos |
| `instalador chat [ALVO] [--fase N] [--rodadas N]` | conversa socrática calibrada pela sua nuance |
| `instalador debate TEMA... [--alvo ALVO]` | Cético × Convicto × Juiz ao vivo no terminal |
| `instalador status` | agentes, motor de IA, versão |
| `instalador instale` / `desinstale` | wrapper em `~/.local/bin` |
| `instalador arte` | o banner em tamanho grande |
| `instalador versao` | versão |

Opções: `-o DIR` (onde escrever a saída), `--sem-ia` (força o motor determinístico),
`--json` (`destri`: mapa puro, sem narrativa), `--mapa ARQ` (`chat`: reaproveita um
`mapa.json` já gerado em vez de reescanear).

## Os seis agentes

| Agente | Função | Entra com | Sai com |
|---|---|---|---|
| **Destripador** | lê o alvo inteiro: arquivos, linguagens, símbolos, imports, riscos, pontos fortes | caminho (pasta ou arquivo) | mapa estrutural com evidências |
| **Professor** | transforma o mapa em curso: 6 fases, complexo → simples | mapa + veredito | o curso em blocos tipados |
| **Cético** | objeta cada ponto com evidência de arquivo:linha | mapa | objeções niveladas (crítico→baixo) |
| **Convicto** | defende a explicação mais forte, também com evidência | mapa | defesas com endereço |
| **Juiz** | pontua objeções × defesas e decide se o material ensina | objeções + defesas | veredito + confiança 0–100 |
| **Sócrates** | não responde: pergunta; calibra o nível 1–5 pelo jargão, hesitação e extensão da sua resposta | você | perguntas que afiam a fase atual |

Material nenhum vira ensino **antes do tribunal**: a Fase 5 (“Onde quebra”) é o debate
transcrito, e o selo do Juiz fica estampado na capa do PDF, no DOCX, no markdown e no vault.

## O que `curso` gera

| Arquivo | Formato | Quem consome |
|---|---|---|
| `curso.pdf` | PDF A4: capa, sumário, código em monoespaçada | humano (imprimir, enviar) |
| `curso.docx` | Word de verdade (OOXML) | humano (editar, comentar) |
| `curso.md` | markdown com H2 por fase + índice JSON no fim | **outros agentes (Codex, Claude, Cursor)** |
| `mapa.json` | estrutura completa com evidência arquivo:linha | máquinas |
| `mapa.mmd` | grafo de dependências (mermaid) | Obsidian / GitHub / ferramentas de diagrama |
| `curso.mmd` | o próprio curso como fluxo (mermaid) | idem |
| `obsidian/` | vault: MOC, nota por fase, veredito, mapa — wikilinks que sempre resolvem | Obsidian |

### Pronto para usar em outro agente

```text
Leia curso.md completo (e mapa.json quando precisar de evidência).
Explique a Fase 3 em 5 bullets como se eu nunca tivesse visto este código.
Depois me faça 3 perguntas de prova — eu respondo, você corrige.
```

```text
Usando mapa.json, gere um quiz de 10 perguntas de múltipla escolha sobre as fases 1–4,
com gabarito comentado apontando arquivo:linha.
```

```text
Compare a Fase 5 (onde quebra) deste curso com o estado atual do repositório.
Que riscos novos apareceram desde a geração?
```

## Conversa com nuance semântica

`instalador chat` mede como você fala — jargão técnico, hesitação, extensão da
resposta — e recalibra a pergunta seguinte: quem responde como engenheiro escuta
pergunta de engenheiro (nível 5); quem hesita recebe analogia e pergunta simples
(nível 1). O Sócrates nunca dá a resposta: aponta para onde a resposta está no código.

```
Sócrates › Quando o programa começa a rodar, qual a PRIMEIRA coisa que acontece?
> abre o main, importa o util
Sócrates › E o que acontece no instante em que um número inexistente chega à tabela?
```

## O tribunal (e a matemática dele)

Nada de opinião solta: toda objeção tem peso, toda defesa tem ganho.

| Nível do risco | Peso na pena |
|---|---|
| crítico (credencial em claro, eval/exec, chave reconhecível) | 8 |
| alto (shell=True, SQL por concatenação, innerHTML) | 5 |
| médio (except genérico, DEBUG=True, CORS aberto, http sem TLS) | 2 |
| baixo (TODO/FIXME/HACK) | 1 |

```
pena      = soma dos pesos das objeções
ganho     = min(10, 2 × número de defesas)
confiança = clamp(90 − pena + ganho, 5, 99)

>= 80  -> material sólido: explicar como está, citando as ressalvas
>= 55  -> aceito com ressalvas: ensinar primeiro as objeções marcadas
<  55  -> questionado: o aluno vê onde quebra ANTES do caminho feliz
```

A barra de 20 blocos (`████████░░░░░░░░░░░░`) aparece na capa, no veredito e no
rodapé das fases — no PDF, no DOCX, no markdown e no vault.

## IA opcional (o curso existe sem ela)

Tudo roda no motor determinístico — heurística real sobre o código, nenhum modelo
obrigatório. Com um modelo por perto, as prosas (analogias, objeções extras,
resumos) ficam melhores; sem, nada cai:

| Variável | Efeito |
|---|---|
| `OLLAMA_HOST` (+ `OLLAMA_MODEL`) | Ollama local (padrão `llama3.2`); porta 11434 aberta já ativa |
| `OPENAI_API_KEY` (+ `OPENAI_MODEL`) | OpenAI (padrão `gpt-4o-mini`) |
| `OPENROUTER_API_KEY` (+ `OPENROUTER_MODEL`) | OpenRouter |
| `INSTALADOR_SEM_IA=1` | força offline (é o que os testes usam) |

Ordem de preferência: Ollama → OpenAI → OpenRouter → silêncio.

## Testes

```bash
python3 -m unittest discover -s testes -v
```

19 testes: arte, mapa, debate, socrático, curso, PDF (validado com pypdf),
DOCX (validado com python-docx), mermaid, vault Obsidian (todo wikilink resolvido),
CLI por subprocess e a calculadora de exemplo.

## Estrutura

```
Instalador/
├── instalador               # o executável (CLI)
├── agentes/                 # OS SEIS AGENTES — um arquivo por agente
│   ├── destripador.py       # Destripador — lê tudo, vira mapa estrutural
│   ├── professor.py         # Professor — 6 fases, complexo → simples
│   ├── cetico.py            # Cético — objeta com evidência
│   ├── convicto.py          # Convicto — defende com evidência
│   ├── juiz.py              # Juiz — pontua e decide
│   └── socrates.py          # Sócrates — pergunta e calibra
├── instalador_core/         # motores: leitura, análise e saídas (PDF/DOCX/Obsidian)
│   ├── arte.py              # a fonte de blocos GENIAL LABS
│   ├── leitura.py           # caminhada de arquivos, linguagens, símbolos
│   ├── analise.py           # riscos (com evidência) e pontos fortes
│   ├── llm.py               # Ollama → OpenAI → OpenRouter → offline
│   ├── pdf.py               # PDF feito à mão (só stdlib)
│   ├── docx.py              # DOCX/OOXML feito à mão (só stdlib)
│   ├── mermaid.py           # mapa.mmd e curso.mmd
│   ├── obsidian.py          # o vault
│   └── relatorios.py        # curso.md para agentes + orquestra os 7 artefatos
├── exemplos/calculadora/    # demo com falhas plantadas
├── testes/                  # suite offline
├── install.sh · install.ps1 · uninstall.sh · uninstall.ps1
├── LICENSE (MIT) · VERSION · .gitattributes · .gitignore
└── README.md · AGENTES.md
```


## Licença

MIT — Genial Labs AI. Veja `LICENSE`.
