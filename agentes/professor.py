# -*- coding: utf-8 -*-
"""Professor — transforma o mapa destrinchado em um curso de 6 fases.

Regra da casa: complexo entra, simples sai. Cada fase tem um objetivo
declarado, blocos concretos ancorados no código real (arquivo:linha) e um
fecho que diz o que o aluno PRECISA saber fazer ao terminar. Com backend
de IA disponível, cada fase ganha uma "nota do professor"; sem IA, o
motor heurístico entrega o curso inteiro."""
import json

from instalador_core import llm
from .socrates import Socrates

SLUGS = [
    "visao-geral",
    "anatomia",
    "logica-principal",
    "contratos-e-dados",
    "onde-quebra",
    "pratica",
]

TITULOS = [
    "Visão geral — o que é isto e para que serve",
    "Anatomia — as peças e quem fala com quem",
    "Lógica principal — o caminho do dado",
    "Contratos e dados — formatos, fronteiras e promessas",
    "Onde quebra — o tribunal: Cético × Convicto × Juiz",
    "Prática — exercícios, erros esperados e perguntas que travam",
]

OBJETIVOS = [
    "Explicar em 3 frases, sem jargão, o que este projeto faz e para quem ele existe.",
    "Apontar no diagrama cada peça do projeto e dizer em uma frase o trabalho dela.",
    "Rastrear, em voz alta, UMA execução concreta do começo ao fim, sem pular etapas.",
    "Nomear os formatos que circulam no sistema e onde termina a confiança no dado de fora.",
    "Defender cada escolha arquitetônica — ou apontar exatamente onde você mudaria.",
    "Rodar, quebrar de propósito e consertar; e responder às perguntas do fim sem travar.",
]

_ANALOGIAS = [
    (("flask", "fastapi", "django", "express", "api", "server", "route", "rota", "http", "endpoint"),
     "Pense num restaurante: o código é a cozinha, a API é o balcão, as rotas são o cardápio. "
     "Todo pedido entra pelo balcão, alguém decide o prato, a cozinha monta e devolve pelo mesmo balcão. "
     "Ninguém na sala precisa saber onde fica a panela — mas quando o prato chega frio, a culpa é do balcão ou da cozinha?"),
    (("argparse", "cli", "comando", "console", "terminal", "script", "shell"),
     "Pense numa caixa de ferramentas: cada subcomando é uma ferramenta com o manuseio escrito no cabo. "
     "Quem pega a ferramenta certa faz o serviço; quem aperta sem ler o cabo, machuca a mão. "
     "O README é o guia de montagem da caixa — se ele faltou peça, a caixa tem buraco."),
    (("sql", "sqlite", "postgres", "mysql", "banco", "db", "orm"),
     "Pense num cartório: tudo tem ficha, tudo tem dono, e toda entrada e saída passa por uma única porta — a consulta. "
     "A confusão nasce quando alguém começa a rasurar a ficha por trás da porta, montando a consulta com cola e texto."),
    (("calc", "mat", "num", "float", "int", "math", "price", "preco"),
     "Pense na balança de feira: cada operação é uma ponta, e o resultado só é verdade se a tareia estiver zerada. "
     "Erro de arredondamento é o grão de areia que muda a conta no fim do dia — pequeno, mas soma."),
]
ANALOGIA_PADRAO = (
    "Pense num relógio suíço: dezenas de peças pequenas, cada uma com uma função curta e um lugar fixo. "
    "O segredo não está em nenhuma peça — está no encaixe. Entender o projeto é aprender onde cada peça encaixa, "
    "e o que acontece quando uma gira fora da hora.")

STDLIB = {
    "os", "sys", "json", "re", "math", "datetime", "argparse", "subprocess", "collections",
    "itertools", "functools", "pathlib", "typing", "dataclasses", "unittest", "logging",
    "time", "io", "csv", "hashlib", "random", "socket", "struct", "tempfile", "urllib",
    "abc", "enum", "traceback", "shutil", "glob", "platform", "string", "textwrap",
    "copy", "operator", "base64", "zlib", "zipfile", "email", "html", "xml", "asyncio",
    "threading", "multiprocessing", "sqlite3", "decimal", "fractions", "statistics",
}


def _slug_ok(n):
    return SLUGS[n - 1]


def analogia_para(mapa):
    pilha = " ".join(list(mapa.get("linguagens", {}).keys())) + " "
    pilha += " ".join(a["caminho"].lower() for a in mapa.get("arquivos", []))
    pilha += " " + " ".join(i for a in mapa.get("arquivos", []) for i in a.get("imports", []))
    pilha += " " + (mapa.get("resumo") or "").lower()
    for chaves, texto in _ANALOGIAS:
        if any(c in pilha.lower() for c in chaves):
            return texto
    return ANALOGIA_PADRAO


REMEDIOS = {
    "credencial em claro": "mover para variável de ambiente ou gerenciador de segredos — e rodar o histórico por git filter-repo",
    "chave reconhecível": "rodar o escâner de segredos, rotacionar a chave agora e bloquear o padrão no pre-commit",
    "eval/exec": "trocar por parsing explícito ou ramificações nomeadas — código que escreve código precisa de portão",
    "SQL por string": "usar placeholders (parâmetros) em vez de f-string — a entrada nunca entra crua na consulta",
    "shell=True": "passar lista de argumentos e validar os valores que vêm de fora — metacaractere vira comando",
    "innerHTML": "sanitizar ou usar textContent/innerHTML apenas com dado seu — o navegador não é seu juiz de confiança",
    "except sem detalhe": "capturar a exceção específica, logar com contexto e decidir: repetir, degradar ou parar",
    "DEBUG=True": "virar variável de ambiente — debug ligado em produção vira vitrine de erro",
    "CORS *": "fechar para a origem real — estrela no CORS significa qualquer site pode bater na porta",
    "http sem TLS": "trocar para https quando o destino é público — pacotes de ônibus entregam conteúdo errado",
    "TODO/FIXME": "abrir issue com o número no comentário — dívida sem dono vira herança",
}

PAPIS_POR_NOME = [
    (("main", "app", "server", "cli", "entry", "instala", "genial"), "ponto de entrada / orquestração"),
    (("test",), "testes — o seguro contra regressão"),
    (("util", "helper", "common", "base"), "apoio genérico"),
    (("config", "conf", "settings", "const"), "configuração e constantes"),
    (("model", "schema", "dao"), "dados e contratos persistidos"),
    (("view", "template", "ui", "render"), "apresentação"),
]


def _papel_de(a):
    base = a["caminho"].lower()
    for chaves, papel in PAPIS_POR_NOME:
        if any(c in base for c in chaves):
            return papel
    lingua = a.get("linguagem", "")
    if lingua in ("Markdown", "RST"):
        return "documentação"
    if lingua in ("JSON", "YAML", "TOML"):
        return "dados / configuração"
    if a.get("simbolos"):
        tops = [s["nome"] for s in a["simbolos"][:3]]
        return "módulo (principais: %s)" % ", ".join(tops)
    return "módulo"


def _fatos_curtos(mapa, limite=900):
    return json.dumps({
        "nome": mapa.get("nome"),
        "resumo": (mapa.get("resumo") or "")[:240],
        "linguagens": mapa.get("linguagens"),
        "dominante": mapa.get("dominante"),
        "top": [a["caminho"] for a in sorted(mapa.get("arquivos", []), key=lambda x: -x["linhas"])[:6]],
    }, ensure_ascii=False)[:limite]


class Professor:
    nome = "Professor"
    papel = "transforma o mapa destrinchado em 6 fases didáticas, complexo → simples, com objetivo declarado por fase"

    def ensinar(self, mapa, juizo, sem_ia=False, ao_avisar=None):
        if ao_avisar:
            ao_avisar("montando as 6 fases", 0, 6)
        fases = []
        for n in range(1, 7):
            if ao_avisar:
                ao_avisar("escrito %d/6: %s" % (n, TITULOS[n - 1].split(" — ")[0]), n, 6)
            blocos = getattr(self, "_fase%d" % n)(mapa, juizo)
            nota_ia = self._nota_ia(mapa, n, sem_ia)
            if nota_ia:
                blocos.insert(1, {"tipo": "nota", "autor": "Nota do Professor", "texto": nota_ia})
            fases.append({
                "n": n,
                "slug": _slug_ok(n),
                "titulo": TITULOS[n - 1],
                "objetivo": OBJETIVOS[n - 1],
                "blocos": blocos,
            })
        return {
            "titulo": "Curso: %s" % mapa.get("nome", "projeto"),
            "subtitulo": "Gerado pelo Instalador (Genial Labs) — %s" % mapa.get("gerado_em", ""),
            "alvo": mapa.get("raiz", ""),
            "gerado_em": mapa.get("gerado_em", ""),
            "versao_instalador": __import__("instalador_core", fromlist=["__version__"]).__version__,
            "meta": {
                "nome": mapa.get("nome"),
                "arquivos_total": mapa.get("arquivos_total", 0),
                "linhas_total": mapa.get("linhas_total", 0),
                "dominante": mapa.get("dominante"),
                "linguagens": mapa.get("linguagens", {}),
                "resumo": mapa.get("resumo", ""),
                "cobertura_doc": mapa.get("cobertura_doc"),
            },
            "analogia": analogia_para(mapa),
            "fases": fases,
            "juizo": juizo,
            "prompts": [
                "Leia curso.md completo. Explique a fase 3 em 5 bullets como se eu nunca tivesse visto este código.",
                "Usando mapa.json, gere um quiz de 10 perguntas de múltipla escolha sobre as fases 1–4, com gabarito comentado.",
                "Compare a Fase 5 (onde quebra) deste curso com o estado atual do repositório. Que riscos novos apareceram desde a geração?",
            ],
        }

    # ------------------------------------------------------------------ #

    def _nota_ia(self, mapa, n, sem_ia):
        if sem_ia:
            return None
        det = llm.detectar()
        if not det:
            return None
        txt = llm.chamar(
            "Você é o Professor do Genial Labs, instalador terminal. Escreva em português do Brasil, "
            "tom didático e direto, no máximo 3 frases curtas. Sem listas, sem saudação, sem repetir o título.",
            "Fase %d (%s) do curso sobre: %s. Contexto: %s" % (
                n, TITULOS[n - 1], mapa.get("resumo", "?")[:200], _fatos_curtos(mapa, 600)),
            max_caracteres=420, timeout=45)
        return txt.strip() if txt else None

    # ------------------------------------------------------------------ #

    def _fase1(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": mapa.get("resumo", "Este é o material analisado.")})
        langs = ", ".join("%s (%d)" % kv for kv in (mapa.get("linguagens") or {}).items()) or "?"
        b.append({"tipo": "p", "texto": "Em escala: **%s arquivos**, **%s linhas**, dominante **%s**. Linguagens: %s." % (
            mapa.get("arquivos_total", 0), mapa.get("linhas_total", 0), mapa.get("dominante") or "?", langs)})
        b.append({"tipo": "h2", "texto": "A analogia"})
        b.append({"tipo": "p", "texto": analogia_para(mapa)})
        b.append({"tipo": "nota", "texto": "A analogia é guarda-chuva, não contrato: ela vai falhar em algum ponto. O ponto onde ela quebra é exatamente onde o sistema tem comportamento interessante — guarde para a Fase 5."})
        b.append({"tipo": "h2", "texto": "Por onde começar a ler"})
        sug = []
        for cam in (mapa.get("leitura_sugerida") or [])[:8]:
            meta = next((a for a in mapa["arquivos"] if a["caminho"] == cam), None)
            linhas = meta["linhas"] if meta else "?"
            b_ = {"tipo": "lista_item", "texto": "`%s` — %s linhas — %s" % (cam, linhas, _papel_de(meta) if meta else "consulte o mapa")}
            sug.append(b_)
        b.extend(sug)
        b.append({"tipo": "p", "texto": "Feche esta fase com a prova: explique em voz alta, para alguém fora da equipe, em 3 frases o que este projeto faz e quem sente a dor quando ele quebra."})
        return b

    def _fase2(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": "Toda casa tem planta. Esta é a planta do material: cada peça, o tamanho dela e o papel que cumpre. O tamanho importa: peça gigante esconde três trabalhos."})
        tops = sorted(mapa.get("arquivos", []), key=lambda a: -a["linhas"])[:14]
        cab = ["Peça", "Linhas", "Linguagem", "Papel inferido"]
        linhas = [[a["caminho"], str(a["linhas"]), a.get("linguagem", "?"), _papel_de(a)] for a in tops]
        b.append({"tipo": "tabela", "cab": cab, "linhas": linhas})
        b.append({"tipo": "p", "texto": "O grafo abaixo liga quem importa quem (arestas reais extraídas dos imports). Nó tracejado/grosso é o ponto de partida sugerido; cores marcam densidade de risco."})
        b.append({"tipo": "codigo", "titulo": "mapa.mmd — estrutura do material (diagrama mermaid, renderiza no Obsidian/GitHub)",
                  "linhas": _le_mmd_mapa(mapa)})
        b.append({"tipo": "nota", "texto": "Regra de leitura: siga a aresta a partir do ponto de partida. Se uma peça não aparece ligada a nada, ela é ilhada — ou órfã, ou futura. Ambas merecem pergunta."})
        return b

    def _fase3(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": "Não memorize a lista de funções: acompanhe UM dado real do começo ao fim. É a diferença entre decorar o mapa e ter andado pela cidade."})
        _nao_codigo = ("Markdown", "RST", "JSON", "YAML", "TOML", "CSV", "Outro")
        codigos = [c for c in mapa.get("leitura_sugerida", [])
                   if next((a["linguagem"] for a in mapa["arquivos"] if a["caminho"] == c), "") not in _nao_codigo]
        entry = (codigos or [x for x in (mapa.get("leitura_sugerida") or [""]) if x])[0]
        meta = next((a for a in mapa["arquivos"] if a["caminho"] == entry), None)
        if meta:
            b.append({"tipo": "h2", "texto": "O coração: `%s`" % meta["caminho"]})
            shown = 0
            for s in meta.get("simbolos", []):
                if s["tipo"] not in ("funcao", "classe"):
                    continue
                if shown >= 8:
                    break
                shown += 1
                if s["tipo"] == "classe":
                    assinatura = "class %s" % s["nome"]
                    extra = " — métodos: %s" % ", ".join(s.get("metodos", [])[:10]) if s.get("metodos") else ""
                else:
                    argumentos = ", ".join(s.get("args", []))
                    assinatura = "%s(%s)" % (s["nome"], argumentos)
                b.append({"tipo": "codigo", "linhas": [assinatura + extra if False else assinatura + ("  # " + s["doc"] if s.get("doc") else "")]})
                if s.get("doc"):
                    b.append({"tipo": "p", "texto": "Docstring: “%s”." % s["doc"]})
                else:
                    b.append({"tipo": "p", "texto": "Sem docstring — o contrato mora na implementação. Leia a primeira decisão dela: é ali que o dado divide o mundo em caminhos."})
        else:
            b.append({"tipo": "p", "texto": "Nenhum ponto de entrada foi reconhecido pelo nome. Abra o maior arquivo da Fase 2 e localize a chamada raiz (main, if __name__, export default)."})
        b.append({"tipo": "h2", "texto": "O esqueleto do fluxo"})
        b.append({"tipo": "p", "texto": "Em qualquer sistema, o caminho feliz tem quatro atos: **entrada** (o dado cru chega), **decisão** (uma ramificação divide o mundo), **transformação** (o dado ganha forma nova), **saída** (volta para quem pediu). Localize cada ato acima; quem não existir é porquê bom para entrevista técnica."})
        b.append({"tipo": "nota", "texto": "Prova de fogo desta fase: traça em voz alta UMA execução concreta do começo ao fim, nomeando arquivo e função em cada passo. Se travou, volta no passo anterior — não pula."})
        return b

    def _fase4(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": "Contrato é promessa entre peças: o formato que entra, o formato que sai, o que é confiável e o que vem de fora. Sistema grande raramente quebra por bug de lógica — quebra por contrato violado em silêncio."})
        dados = [a for a in mapa.get("arquivos", []) if a.get("linguagem") in ("JSON", "YAML", "TOML", "CSV")]
        if dados:
            b.append({"tipo": "h2", "texto": "Formatos que circulam"})
            for a in dados[:6]:
                chaves = [s["nome"] for s in a.get("simbolos", []) if s["tipo"] == "chave/topo"][:10]
                b.append({"tipo": "p", "texto": "`%s` — chaves de topo: %s" % (a["caminho"], ", ".join("`%s`" % c for c in chaves) or "(vazio ou aninhado)")})
        ext = {}
        for a in mapa.get("arquivos", []):
            for imp in a.get("imports", []):
                topo = imp.split(".")[0].split("/")[0]
                if topo and not topo.startswith(".") and not topo.startswith("/"):
                    ext[topo] = ext.get(topo, 0) + 1
        if ext:
            b.append({"tipo": "h2", "texto": "Dependências externas"})
            ordem = sorted(ext.items(), key=lambda kv: -kv[1])[:16]
            b.append({"tipo": "tabela", "cab": ["Pacote/módulo", "Usado por", "Origem"],
                      "linhas": [[k, str(v), "stdlib" if k in STDLIB else "externa — verificar versão em lockfile"] for k, v in ordem]})
        b.append({"tipo": "h2", "texto": "Onde termina a confiança"})
        b.append({"tipo": "p", "texto": "Toda variável que vem de fora (usuário, rede, arquivo, clock) é inimiga até ser validada. Percorra a lista de riscos da próxima fase e pergunte de cada um: qual dado externo chega aqui sem inspeção?"})
        b.append({"tipo": "nota", "texto": "Marca de amadurecimento: você não confia em input — você confere. 'Confio' é adjetivo de iniciante."})
        return b

    def _fase5(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": "Todo material passa pelo tribunal antes de virar ensino. O Cético ataca com evidência (arquivo:linha), o Convicto defende com o que existe de bom, e o Juiz fecha com pontuação aberta — nada de achismo com cara de laudo."})
        b.append({"tipo": "h2", "texto": "Objeções do Cético"})
        for o in juizo.get("objecoes", []):
            ev = o.get("evidencia", "")
            b.append({"tipo": "lista_item", "risco": o.get("nivel", ""),
                      "texto": "**[%s]** %s%s" % (o.get("nivel", "?").upper(), o.get("texto", ""), (" — `%s`" % ev) if ev else "")})
        if not juizo.get("objecoes"):
            b.append({"tipo": "p", "texto": "O Cético não encontrou objeção com evidência — o que, em si, é informação: ou o material é limpo, ou a análise cobriu menos do que parece."})
        b.append({"tipo": "h2", "texto": "Defesas do Convicto"})
        for d in juizo.get("defesas", []):
            ev = d.get("evidencia", "")
            b.append({"tipo": "lista_item", "defesa": True,
                      "texto": "%s%s" % (d.get("texto", ""), (" (`%s`)" % ev) if ev else "")})
        b.append({"tipo": "h2", "texto": "Veredito do Juiz"})
        barra_ascii = barra_juiz(juizo.get("confianca", 0))
        b.append({"tipo": "codigo", "titulo": "confiança do material", "linhas": [barra_ascii, "%d/100  |  %s" % (juizo.get("confianca", 0), juizo.get("decisao", ""))]})
        b.append({"tipo": "p", "texto": juizo.get("resumo", "")})
        b.append({"tipo": "h2", "texto": "O que consertar primeiro"})
        riscos = sorted(juizo.get("objecoes", []), key=lambda o: {"critico": 0, "alto": 1, "medio": 2, "baixo": 3}.get(o.get("nivel", "baixo"), 4))[:6]
        if riscos:
            for r in riscos:
                remedio = REMEDIOS.get(_titulo_proximo(r.get("texto", "")), "tratar como incidente: reproduzir, isolar, corrigir, registrar")
                b.append({"tipo": "lista_item", "texto": "**%s** — %s" % (r.get("texto", "")[:110], remedio)})
        else:
            b.append({"tipo": "p", "texto": "Nada urgente. Mantenha o hábito: rode a análise de novo a cada mudança relevante — risco novo quase sempre chega junto de feature nova."})
        return b

    def _fase6(self, mapa, juizo):
        b = []
        b.append({"tipo": "p", "texto": "Teoria sem calos é boato. Esta fase é onde o curso vira habilidade: você roda, quebra, conserta e explica. Quem só leu não sabe nada ainda."})
        dom = (mapa.get("dominante") or "").lower()
        entry = (mapa.get("leitura_sugerida") or ["o ponto de entrada"])[0]
        comandos = {
            "python": "python3 %s --help  (depois: uma execução real com dados seus)" % entry,
            "javascript": "node %s", "typescript": "npx ts-node %s" % entry,
            "shell": "sh %s", "powershell": "powershell -File %s" % entry,
        }
        cmd = comandos.get(dom, "localize o comando de execução (README, makefile, package.json)")
        b.append({"tipo": "h2", "texto": "Exercícios"})
        b.append({"tipo": "lista_item", "exercicio": 1, "texto": "**Rode de verdade.** %s" % cmd})
        b.append({"tipo": "lista_item", "exercicio": 2, "texto": "**Quebre de propósito.** Mude uma condição de borda (valor mágico, limite, default) e observe o estrago ANTES de tentar consertar."})
        b.append({"tipo": "lista_item", "exercicio": 3, "texto": "**Explique para uma criança de 10 anos.** Proibido jargão. Se travou, o jargão estava escondendo o raciocínio."})
        b.append({"tipo": "lista_item", "exercicio": 4, "texto": "**Escreva um teste** para a função mais chamativa da Fase 3 — incluindo o caso que a Faz 5 marca como risco."})
        b.append({"tipo": "lista_item", "exercicio": 5, "texto": "**Aplique UM remédio** da Fase 5. Depois rode a análise de novo e veja a pontuação do Juiz mudar."})
        b.append({"tipo": "h2", "texto": "Perguntas que você deve saber responder"})
        soc = Socrates()
        ctx = soc.contexto(mapa)
        from . import socrates as _soc
        for _, tpl in _soc.BANCO.get(6, []):
            b.append({"tipo": "lista_item", "pergunta": True, "texto": soc._preencher(tpl, ctx)})
        b.append({"tipo": "h2", "texto": "Checklist de conclusão"})
        for item in [
            "Explico o projeto em 3 frases para leigo — sem jargão",
            "Aponto cada peça no diagrama e digo o trabalho dela",
            "Rastrei uma execução completa nomeando arquivo e função",
            "Nomeei os contratos de dado e onde termina a confiança",
            "Defendi (ou ataquei com endereço) cada escolha discutida na Fase 5",
            "Rodei, quebrei e consertei pelo menos uma vez",
        ]:
            b.append({"tipo": "checklist", "texto": item})
        return b


def _le_mmd_mapa(mapa):
    try:
        from instalador_core import mermaid
        return mermaid.mapa_mermaid(mapa).splitlines()
    except Exception:
        linhas = ["flowchart TD"]
        for s in mapa.get("grafo", [])[:20]:
            linhas.append("    %s --> %s" % tuple(x.replace("/", "-").replace(".", "-") for x in s))
        return linhas


def barra_juiz(confianca, tamanho=24):
    cheio = int(round(confianca / 100.0 * tamanho))
    return "#" * cheio + "-" * (tamanho - cheio)


def _titulo_proximo(texto):
    t = texto.lower()
    melhor, melhor_hits = "", 0
    for chave in REMEDIOS:
        palavras = [w for w in chave.lower().replace("-", " ").split() if len(w) > 3]
        hits = sum(1 for w in palavras if w in t)
        if hits > melhor_hits:
            melhor, melhor_hits = chave, hits
    return melhor if melhor_hits >= 2 else (melhor if melhor_hits == 1 and len(REMEDIOS) else melhor)
