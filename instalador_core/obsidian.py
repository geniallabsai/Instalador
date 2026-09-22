# -*- coding: utf-8 -*-
"""Vault Obsidian do curso: uma pasta para arrastar direto na aplicação.

Convenções usadas (testadas pelo suíte):
- frontmatter YAML em todas as notas;
- [[wikilinks]] que SEMPRE resolvem para uma nota existente;
- callouts nativos [!note]/[!warning]/[!danger] para riscos;
- mermaid embutido em fence nativo;
- 00-moc = mapa de conteúdo (índice vivo)."""
import os


def _front(**kv):
    linhas = ["---"]
    for k, v in kv.items():
        linhas.append("%s: %s" % (k, _yaml(v)))
    linhas.append("---")
    return "\n".join(linhas)


def _yaml(v):
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[%s]" % ", ".join(str(x) for x in v)
    s = str(v).replace('"', "'")
    return '"%s"' % s


def _md_bloco(b):
    """Renderiza um bloco do curso como markdown Obsidian."""
    tipo = b.get("tipo")
    if tipo == "p":
        return b.get("texto", "")
    if tipo == "h2":
        return "## " + b.get("texto", "")
    if tipo == "lista_item":
        pref = "- "
        if b.get("exercicio"):
            pref = "%d. " % b["exercicio"]
        if b.get("pergunta"):
            pref = "> ? "
        return pref + b.get("texto", "")
    if tipo == "checklist":
        return "- [ ] " + b.get("texto", "")
    if tipo == "codigo":
        titulo = ("<!-- %s -->\n" % b["titulo"]) if b.get("titulo") else ""
        return ("%s\n```\n%s\n```" % (titulo, "\n".join(b.get("linhas", []))))
    if tipo == "tabela":
        cab = b.get("cab", [])
        linhas = b.get("linhas", [])
        saida = ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] * len(cab)) + "|"]
        for l in linhas:
            saida.append("| " + " | ".join(str(x) for x in l) + " |")
        return "\n".join(saida)
    if tipo == "nota":
        corpo = ("> " + b.get("texto", "").replace("\n", "\n> "))
        if b.get("autor"):
            corpo = "> **" + b["autor"] + "**\n" + corpo
        return corpo
    return str(b.get("texto", ""))


def gerar_vault(diretorio, curso, mapa, mmd_mapa, mmd_curso):
    juizo = curso.get("juizo", {})
    nomes = {"moc": "00-moc"}
    nomes.update({"veredito": "veredito-do-juiz", "mapa": "mapa-estrutural"})
    for f in curso["fases"]:
        nomes["fase%d" % f["n"]] = "%02d-%s" % (f["n"], f["slug"])

    os.makedirs(diretorio, exist_ok=True)
    criados = []

    def gravar(nome, conteudo):
        caminho = os.path.join(diretorio, nome + ".md")
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(conteudo + "\n")
        criados.append(caminho)

    # ---------------- fase notes ---------------- #
    for f in curso["fases"]:
        corpo = [_front(tags=["curso", "instalador", "fase-%d" % f["n"]],
                        curso=curso["meta"]["nome"], fase=f["n"],
                        titulo=f["titulo"].split(" — ")[0],
                        gerado_em=curso.get("gerado_em", ""))]
        corpo.append("# Fase %d — %s" % (f["n"], f["titulo"]))
        corpo.append("")
        corpo.append("> [!goal] Objetivo desta fase")
        corpo.append("> " + f["objetivo"])
        corpo.append("")
        for b in f["blocos"]:
            corpo.append(_md_bloco(b))
            corpo.append("")
        nav = []
        if f["n"] > 1:
            nav.append("[[%s|%d — anterior]]" % (nomes["fase%d" % (f["n"] - 1)], f["n"] - 1))
        nav.append("[[00-moc|MOC]]")
        if f["n"] < 6:
            nav.append("[[%s|%d — próxima]]" % (nomes["fase%d" % (f["n"] + 1)], f["n"] + 1))
        corpo.append("* * *")
        corpo.append(" · ".join(nav))
        gravar(nomes["fase%d" % f["n"]], "\n".join(corpo))

    # ---------------- veredito ---------------- #
    v = [_front(tags=["curso", "veredito", "juiz"], curso=curso["meta"]["nome"],
                confianca=juizo.get("confianca", 0), gerado_em=curso.get("gerado_em", ""))]
    v.append("# Veredito do Juiz")
    v.append("")
    v.append("> [!abstract] Confiança do material: **%d/100**" % juizo.get("confianca", 0))
    barra = juizo.get("barra", "")
    v.append("`" + barra + "`")
    v.append("")
    v.append("**Decisão:** %s" % juizo.get("decisao", ""))
    v.append("")
    v.append(juizo.get("resumo", ""))
    v.append("")
    v.append("| Penas | Ganhos |")
    v.append("|---|---|")
    v.append("| %s | %s |" % (juizo.get("pontuacao", {}).get("pena", 0), juizo.get("pontuacao", {}).get("ganho", 0)))
    v.append("")
    v.append("## Objeções do Cético")
    for o in juizo.get("objecoes", []):
        v.append("- **[%s]** %s%s" % (o.get("nivel", "?"), o.get("texto", ""),
                                     (" — `%s`" % o["evidencia"]) if o.get("evidencia") else ""))
    v.append("")
    v.append("## Defesas do Convicto")
    for d in juizo.get("defesas", []):
        v.append("- %s%s" % (d.get("texto", ""), (" (`%s`)" % d["evidencia"]) if d.get("evidencia") else ""))
    v.append("")
    v.append("> [!tip] Como estudar isto")
    v.append("> Leia a Fase 5 primeiro. Só depois de saber onde quebra, volte a ler a Fase 3 — o caminho feliz passa a fazer sentido.")
    v.append("")
    v.append("[[00-moc|MOC]] · [[%s|Fase 5 — onde quebra]]" % nomes["fase5"])
    gravar(nomes["veredito"], "\n".join(v))

    # ---------------- mapa estrutural ---------------- #
    m = [_front(tags=["curso", "mapa", "estrutura"], curso=curso["meta"]["nome"],
                arquivos=mapa.get("arquivos_total", 0), linhas=mapa.get("linhas_total", 0),
                dominante=mapa.get("dominante", "?"))]
    m.append("# Mapa Estrutural")
    m.append("")
    m.append("Gerado em %s · %d arquivos · %d linhas · dominante: **%s**" % (
        mapa.get("gerado_em", "?"), mapa.get("arquivos_total", 0), mapa.get("linhas_total", 0), mapa.get("dominante", "?")))
    m.append("")
    m.append("## Diagrama")
    m.append("```mermaid")
    m.append(mmd_mapa)
    m.append("```")
    m.append("")
    m.append("## Peças (maiores primeiro)")
    m.append("| Caminho | Linhas | Linguagem |")
    m.append("|---|---|---|")
    for a in sorted(mapa.get("arquivos", []), key=lambda x: -x["linhas"])[:20]:
        m.append("| `%s` | %d | %s |" % (a["caminho"], a["linhas"], a.get("linguagem", "?")))
    m.append("")
    nivel_callout = {"critico": "danger", "alto": "warning", "medio": "note", "baixo": "info"}
    m.append("## Riscos com evidência")
    if mapa.get("riscos"):
        for r in mapa.get("riscos", [])[:20]:
            m.append("> [%s] **%s** — `%s:%s`" % (nivel_callout.get(r.get("nivel", ""), "note"), r.get("titulo", ""), r.get("arquivo", ""), r.get("linha", "")))
            m.append(">")
            m.append("> `%s`" % r.get("trecho", "").replace("\n", " ")[:160])
            m.append("")
    else:
        m.append("Nenhum risco heurístico encontrado — bom sinal, não prova.")
    m.append("")
    m.append("## Pontos fortes")
    for f_ in mapa.get("fortes", []):
        m.append("- %s — `%s`" % (f_.get("titulo", "?"), f_.get("onde", "")))
    m.append("")
    m.append("[[00-moc|MOC]] · [[%s|Fase 2 — anatomia]]" % nomes["fase2"])
    gravar(nomes["mapa"], "\n".join(m))

    # ---------------- MOC ---------------- #
    moc = [_front(tags=["curso", "instalador", "MOC"], curso=curso["meta"]["nome"],
                  fases=6, confianca=juizo.get("confianca", 0), gerado_em=curso.get("gerado_em", ""))]
    moc.append("# MOC — Curso de %s" % curso["meta"]["nome"])
    moc.append("")
    moc.append("> **Material:** `%s`" % curso.get("alvo", ""))
    moc.append("> **Veredito do Juiz:** confiança **%d/100** — %s" % (juizo.get("confianca", 0), juizo.get("decisao", "")))
    moc.append("> **Gerado:** %s" % curso.get("gerado_em", ""))
    moc.append("")
    moc.append("## Como usar este vault")
    moc.append("")
    moc.append("1. Comece por aqui (esta nota é o índice vivo).")
    moc.append("2. Siga as fases em ordem — cada uma tem objetivo declarado no topo.")
    moc.append("3. A [[veredito-do-juiz|Fase 5]] é a mais valiosa: ela mostra onde o material quebra antes de você herdar a dúvida.")
    moc.append("4. Ao terminar, confira o checklist da [[%s|Fase 6]]." % nomes["fase6"])
    moc.append("")
    moc.append("## O curso em um diagrama")
    moc.append("```mermaid")
    moc.append(mmd_curso)
    moc.append("```")
    moc.append("")
    moc.append("## Fases")
    for f in curso["fases"]:
        moc.append("- [[%s|**Fase %d — %s**]] — %s" % (nomes["fase%d" % f["n"]], f["n"], f["titulo"].split(" — ")[0], f["objetivo"]))
    moc.append("")
    moc.append("## Notas técnicas")
    moc.append("- [[mapa-estrutural|Mapa estrutural]] — grafo, peças, riscos com evidência")
    moc.append("- [[veredito-do-juiz|Veredito do Juiz]] — pontuação aberta do debate Cético × Convicto")
    moc.append("")
    moc.append("## Dando este curso a outro agente")
    moc.append("> [!tip] Prompt pronto")
    moc.append("> \"Leia `curso.md` e `mapa.json` deste curso. Explique a Fase 3 para um iniciante e me faça 5 perguntas antes de eu avançar.\"")
    moc.append("")
    moc.append("| Métrica | Valor |")
    moc.append("|---|---|")
    moc.append("| Arquivos | %d |" % mapa.get("arquivos_total", 0))
    moc.append("| Linhas | %d |" % mapa.get("linhas_total", 0))
    moc.append("| Dominante | %s |" % mapa.get("dominante", "?"))
    moc.append("| Riscos | %d |" % len(mapa.get("riscos", [])))
    moc.append("| Fortes | %d |" % len(mapa.get("fortes", [])))
    gravar(nomes["moc"], "\n".join(moc))

    return criados
