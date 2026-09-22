# -*- coding: utf-8 -*-
"""Relatórios: o curso.md legível por agentes, o PDF, o DOCX e a
orquestração da escrita de TODAS as saídas em uma pasta só.

Contrato de saída do comando `curso` (sempre os sete):
  curso.pdf   — para humanos abrirem/imprimir
  curso.docx  — para humanos editarem
  curso.md    — para agentes (Codex, Claude Code, Cursor): estrutura estável
  mapa.json   — para máquinas (mesmo grafo que alimenta o mermaid)
  obsidian/   — vault pronto para arrastar (MOC + notas por fase)
  mapa.mmd    — diagrama mermaid do material
  curso.mmd   — diagrama mermaid do fluxo do curso
"""
import json
import os

from . import docx as motor_docx
from . import mermaid as motor_mermaid
from . import obsidian as motor_obsidian
from . import pdf as motor_pdf
from .professor import barra_juiz

# ---------------------------------------------------------------------- #
# markdown (agente-consumível e base do vault)                            #
# ---------------------------------------------------------------------- #

def _md_bloco(b):
    tipo = b.get("tipo")
    if tipo == "p":
        return b.get("texto", "")
    if tipo == "h2":
        return "### " + b.get("texto", "")
    if tipo == "lista_item":
        if b.get("exercicio"):
            return "%d. %s" % (b["exercicio"], b.get("texto", ""))
        if b.get("pergunta"):
            return "> ? " + b.get("texto", "")
        return "- " + b.get("texto", "")
    if tipo == "checklist":
        return "- [ ] " + b.get("texto", "")
    if tipo == "codigo":
        cab = ("<!-- %s -->\n" % b["titulo"]) if b.get("titulo") else ""
        return cab + "```\n%s\n```" % "\n".join(b.get("linhas", []))
    if tipo == "tabela":
        cab = b.get("cab", [])
        linhas = b.get("linhas", [])
        saida = ["| " + " | ".join(str(c) for c in cab) + " |",
                 "|" + "|".join(["---"] * len(cab)) + "|"]
        for l in linhas:
            saida.append("| " + " | ".join(str(x) for x in l) + " |")
        return "\n".join(saida)
    if tipo == "nota":
        corpo = "> " + b.get("texto", "").replace("\n", "\n> ")
        if b.get("autor"):
            corpo = "> **" + b["autor"] + "**\n" + corpo
        return corpo
    return str(b.get("texto", ""))


def _indice_json(curso, mapa):
    return {
        "gerador": "Instalador · Genial Labs v%s" % curso.get("versao_instalador", "?"),
        "tipo": "indice-para-agentes",
        "instrucao": "Use este índice para navegar sem ler tudo: 'fases' dá o conteúdo de cada etapa; 'riscos' e 'fortes' têm evidência arquivo:linha.",
        "titulo": curso.get("titulo"),
        "alvo": curso.get("alvo"),
        "gerado_em": curso.get("gerado_em"),
        "fases": [{"n": f["n"], "slug": f["slug"], "titulo": f["titulo"], "objetivo": f["objetivo"]}
                  for f in curso["fases"]],
        "juizo": {"confianca": curso["juizo"].get("confianca"),
                  "decisao": curso["juizo"].get("decisao"),
                  "pontuacao": curso["juizo"].get("pontuacao")},
        "resumo": {
            "arquivos_total": mapa.get("arquivos_total"),
            "linhas_total": mapa.get("linhas_total"),
            "dominante": mapa.get("dominante"),
            "riscos": [{"nivel": r["nivel"], "titulo": r["titulo"], "arquivo": r["arquivo"], "linha": r["linha"]}
                       for r in (mapa.get("riscos") or [])[:12]],
            "fortes": [f.get("titulo") for f in (mapa.get("fortes") or [])],
        },
    }


def md_curso(curso, mapa, mmd_mapa, mmd_curso):
    L = []
    L.append("<!-- instalador-curso v%s — gerado para consumo por agentes (Codex, Claude Code, Cursor...). -->" % curso.get("versao_instalador", "?"))
    L.append("<!-- Estrutura estável: H1 = título · H2 = fases · H3 = seções · ```json no final = índice máquina. -->")
    L.append("")
    L.append("# %s" % curso.get("titulo", "Curso"))
    L.append("")
    meta = curso.get("meta", {})
    L.append("| Campo | Valor |")
    L.append("|---|---|")
    L.append("| Alvo | `%s` |" % curso.get("alvo", ""))
    L.append("| Gerado em | %s |" % curso.get("gerado_em", ""))
    L.append("| Escala | %d arquivos · %d linhas |" % (meta.get("arquivos_total", 0), meta.get("linhas_total", 0)))
    L.append("| Linguagem dominante | %s |" % meta.get("dominante", "?"))
    L.append("| Cobertura de docstring | %s |" % ("%.0f%%" % (meta["cobertura_doc"] * 100) if meta.get("cobertura_doc") is not None else "n/d"))
    L.append("| Veredito do Juiz | **%d/100** — %s |" % (curso["juizo"].get("confianca", 0), curso["juizo"].get("decisao", "")))
    L.append("")
    L.append("## Como consumir este curso")
    L.append("")
    L.append("Se você é um agente de IA: leia este arquivo, abra `mapa.json` quando precisar de evidência e responda às perguntas da Fase 6 antes de prosseguir. Prompts prontos:")
    L.append("")
    for p in curso.get("prompts", []):
        L.append("> %s" % p)
    L.append("")
    L.append("## Sumário")
    L.append("")
    for f in curso["fases"]:
        L.append("%d. **%s** — %s" % (f["n"], f["titulo"].split(" — ")[0], f["objetivo"]))
    L.append("")
    for f in curso["fases"]:
        L.append("")
        L.append("## Fase %d — %s" % (f["n"], f["titulo"]))
        L.append("")
        L.append("> **Objetivo ao terminar:** " + f["objetivo"])
        L.append("")
        for b in f["blocos"]:
            L.append(_md_bloco(b))
            L.append("")
    L.append("")
    L.append("## Veredito do Juiz (índice rápido)")
    L.append("")
    jz = curso["juizo"]
    L.append("`%s` — **%d/100** — %s" % (barra_juiz(jz.get("confianca", 0)), jz.get("confianca", 0), jz.get("decisao", "")))
    L.append("")
    L.append("## Diagramas (mermaid)")
    L.append("")
    L.append("### Mapa do material (`mapa.mmd`)")
    L.append("")
    L.append("```mermaid")
    L.append(mmd_mapa)
    L.append("```")
    L.append("")
    L.append("### Fluxo do curso (`curso.mmd`)")
    L.append("")
    L.append("```mermaid")
    L.append(mmd_curso)
    L.append("```")
    L.append("")
    L.append("## Índice máquina (JSON)")
    L.append("")
    L.append("```json")
    L.append(json.dumps(_indice_json(curso, mapa), ensure_ascii=False, indent=1))
    L.append("```")
    return "\n".join(L)


# ---------------------------------------------------------------------- #
# PDF                                                                     #
# ---------------------------------------------------------------------- #

def _cor_risco(nivel):
    return {"critico": motor_pdf.COR_VERMELHO, "alto": (0.80, 0.42, 0.05),
            "medio": motor_pdf.COR_AMBAR}.get(nivel, motor_pdf.COR_CINZA)


def _tabela_linhas(cab, linhas):
    cols = len(cab)
    larg = [min(46, max(len(str(c)), *(len(str(l[i])) for l in linhas)) if linhas else len(str(c))) for i, c in enumerate(cab)]
    saida = ["  ".join(str(c).ljust(larg[i])[:larg[i]] for i, c in enumerate(cab)),
             "  ".join("-" * l for l in larg)]
    for l in linhas:
        saida.append("  ".join(str(l[i]).ljust(larg[i])[:larg[i]] for i in range(cols)))
    return saida


def pdf_curso(curso, mapa, caminho):
    p = motor_pdf.Pdf()
    jz = curso["juizo"]
    meta = curso.get("meta", {})
    # ---------------- capa ---------------- #
    p.y -= 120
    p.texto("GENIAL LABS", "F2", 40, motor_pdf.COR_TITULO, depois=0)
    p.regua(espessura=2.4)
    p.y -= 8
    p.texto("INSTALADOR · CURSO GERADO POR AGENTES", "F4", 13, motor_pdf.COR_ACENTO, depois=26)
    p.texto(curso.get("titulo", "Curso"), "F2", 21, depois=10)
    p.texto("Alvo: %s" % curso.get("alvo", ""), "F1", 10.5, motor_pdf.COR_CINZA, depois=2)
    p.texto("Gerado em %s" % curso.get("gerado_em", ""), "F1", 10.5, motor_pdf.COR_CINZA, depois=2)
    p.texto("%d arquivos · %d linhas · dominante: %s" % (
        meta.get("arquivos_total", 0), meta.get("linhas_total", 0), meta.get("dominante") or "?"),
        "F1", 10.5, motor_pdf.COR_CINZA, depois=2)
    p.texto("Veredito do Juiz: %d/100 — %s" % (jz.get("confianca", 0), jz.get("decisao", "")),
        "F2", 11, motor_pdf.COR_ACENTO, depois=24)
    p.h2("As seis fases")
    for f in curso["fases"]:
        p.texto("%d. %s" % (f["n"], f["titulo"]), "F1", 11, depois=3)
    p.y -= 30
    p.nota("Este curso foi gerado por uma esquadra de agentes socráticos (Destripador, Professor, Cético, Convicto e Juiz). "
           "A Fase 5 contém o debate completo com evidência arquivo:linha — leia-a antes de confiar no material.")
    # ---------------- sumário ---------------- #
    p.quebra_pagina()
    p.h1("Sumário")
    for f in curso["fases"]:
        p.texto("Fase %d — %s" % (f["n"], f["titulo"]), "F2", 12, depois=1)
        p.texto(f["objetivo"], "F4", 9.5, motor_pdf.COR_CINZA, depois=10)
    # ---------------- fases ---------------- #
    for f in curso["fases"]:
        p.quebra_pagina()
        p.h1("Fase %d — %s" % (f["n"], f["titulo"]))
        p.nota("Objetivo ao terminar esta fase: " + f["objetivo"])
        for b in f["blocos"]:
            _pdf_bloco(p, b)
    # ---------------- apêndices ---------------- #
    p.quebra_pagina()
    p.h1("Apêndice A — Diagramas")
    p.texto("O mesmo conteúdo vive em mapa.mmd (material) e curso.mmd (fluxo), renderizáveis no Obsidian, GitHub e mermaid.live.", "F4", 9.5, motor_pdf.COR_CINZA, depois=8)
    p.bloco_codigo(motor_mermaid.mapa_mermaid(mapa).splitlines(), titulo="mapa.mmd")
    p.bloco_codigo(motor_mermaid.curso_mermaid(curso).splitlines(), titulo="curso.mmd")
    p.quebra_pagina()
    p.h1("Apêndice B — Índice máquina")
    p.bloco_codigo(json.dumps(_indice_json(curso, mapa), ensure_ascii=False, indent=1).splitlines(), titulo="json — para agentes")
    p.salvar(caminho)
    return caminho


def _pdf_bloco(p, b):
    tipo = b.get("tipo")
    if tipo == "p":
        p.texto(_md_limpo(b.get("texto", "")), "F1", 10, depois=6)
    elif tipo == "h2":
        p.h2(b.get("texto", ""))
    elif tipo == "codigo":
        p.bloco_codigo(b.get("linhas", []), titulo=b.get("titulo"))
    elif tipo == "tabela":
        p.bloco_codigo(_tabela_linhas(b.get("cab", []), b.get("linhas", [])), titulo="tabela")
    elif tipo == "lista_item":
        nivel = b.get("risco")
        cor = _cor_risco(nivel) if nivel else (motor_pdf.COR_VERDE if b.get("defesa") else motor_pdf.COR_TEXTO)
        p.lista([b.get("texto", "")], cor=cor, marcador="•", depois_extra=None) if False else \
            p.texto(("• " if not b.get("exercicio") else ("%d. " % b["exercicio"])) + _md_limpo(b.get("texto", "")),
                    "F1", 10, cor, depois=3, x_cont=56 + 13)
    elif tipo == "checklist":
        p.texto("[ ] " + _md_limpo(b.get("texto", "")), "F1", 10, depois=3, x_cont=56 + 13)
    elif tipo == "nota":
        p.nota(b.get("texto", ""), autor=b.get("autor"))


def _md_limpo(t):
    """Remove marcadores markdown que não existem no PDF."""
    t = t.replace("**", "").replace("`", "")
    return t


# ---------------------------------------------------------------------- #
# DOCX                                                                    #
# ---------------------------------------------------------------------- #

def docx_curso(curso, mapa, caminho):
    d = motor_docx.Docx()
    jz = curso["juizo"]
    meta = curso.get("meta", {})
    # capa
    d.body.append(motor_docx._par([motor_docx._run("", tam=20)], depois=1600))
    d.texto("GENIAL LABS", tam=56, cor=motor_docx.COR_TITULO, b=True, antes=0, depois=60)
    d.texto("INSTALADOR · CURSO GERADO POR AGENTES", tam=24, cor="B45309", i=True, depois=400)
    d.texto(curso.get("titulo", "Curso"), tam=40, cor=motor_docx.COR_TITULO, b=True, depois=120)
    d.texto("Alvo: %s" % curso.get("alvo", ""), tam=20, cor=motor_docx.COR_CINZA, depois=40)
    d.texto("Gerado em %s" % curso.get("gerado_em", ""), tam=20, cor=motor_docx.COR_CINZA, depois=40)
    d.texto("%d arquivos · %d linhas · dominante: %s" % (
        meta.get("arquivos_total", 0), meta.get("linhas_total", 0), meta.get("dominante") or "?"),
        tam=20, cor=motor_docx.COR_CINZA, depois=40)
    d.texto("Veredito do Juiz: %d/100 — %s" % (jz.get("confianca", 0), jz.get("decisao", "")),
        tam=22, cor="B45309", b=True, depois=400)
    d.h2("As seis fases")
    for f in curso["fases"]:
        d.texto("%d. %s" % (f["n"], f["titulo"]), tam=22, depois=60)
    d.quebra_pagina()
    d.h1("Sumário")
    for f in curso["fases"]:
        d.h2("Fase %d — %s" % (f["n"], f["titulo"]))
        d.texto("Objetivo: " + f["objetivo"], tam=20, cor=motor_docx.COR_CINZA, i=True)
    for f in curso["fases"]:
        d.quebra_pagina()
        d.h1("Fase %d — %s" % (f["n"], f["titulo"]))
        d.nota("Objetivo ao terminar esta fase: " + f["objetivo"])
        for b in f["blocos"]:
            _docx_bloco(d, b)
    d.quebra_pagina()
    d.h1("Apêndice A — Diagramas")
    d.bloco_codigo(motor_mermaid.mapa_mermaid(mapa).splitlines(), titulo="mapa.mmd")
    d.bloco_codigo(motor_mermaid.curso_mermaid(curso).splitlines(), titulo="curso.mmd")
    d.quebra_pagina()
    d.h1("Apêndice B — Índice máquina")
    d.bloco_codigo(json.dumps(_indice_json(curso, mapa), ensure_ascii=False, indent=1).splitlines(), titulo="json")
    d.salvar(caminho)
    return caminho


def _docx_bloco(d, b):
    tipo = b.get("tipo")
    limpo = lambda t: t.replace("**", "").replace("`", "")
    if tipo == "p":
        d.texto(limpo(b.get("texto", "")))
    elif tipo == "h2":
        d.h2(limpo(b.get("texto", "")))
    elif tipo == "codigo":
        d.bloco_codigo(b.get("linhas", []), titulo=b.get("titulo"))
    elif tipo == "tabela":
        d.tabela(b.get("cab", []), [[str(x) for x in l] for l in b.get("linhas", [])])
    elif tipo == "lista_item":
        if b.get("exercicio"):
            d.texto("%d. %s" % (b["exercicio"], limpo(b.get("texto", ""))), depois=80)
        elif b.get("pergunta"):
            d.nota("Pergunta socrática: " + limpo(b.get("texto", "")))
        else:
            cor = "2E7D46" if b.get("defesa") else None
            prefixo = "•  "
            if b.get("risco"):
                cor = {"critico": "C0392B", "alto": "D35400", "medio": "B07D1B"}.get(b.get("risco"), "6B7280")
            d.texto(prefixo + limpo(b.get("texto", "")), cor=cor, depois=60)
    elif tipo == "checklist":
        d.texto("[ ] " + limpo(b.get("texto", "")), depois=50)
    elif tipo == "nota":
        d.nota(limpo(b.get("texto", "")), autor=b.get("autor"))


# ---------------------------------------------------------------------- #
# orquestração                                                            #
# ---------------------------------------------------------------------- #

def escrever_tudo(base, curso, mapa, mmd_mapa=None, mmd_curso=None):
    os.makedirs(base, exist_ok=True)
    mmd_mapa = mmd_mapa or motor_mermaid.mapa_mermaid(mapa)
    mmd_curso = mmd_curso or motor_mermaid.curso_mermaid(curso)
    caminhos = {}
    caminhos["pdf"] = os.path.join(base, "curso.pdf")
    pdf_curso(curso, mapa, caminhos["pdf"])
    caminhos["docx"] = os.path.join(base, "curso.docx")
    docx_curso(curso, mapa, caminhos["docx"])
    caminhos["md"] = os.path.join(base, "curso.md")
    with open(caminhos["md"], "w", encoding="utf-8") as f:
        f.write(md_curso(curso, mapa, mmd_mapa, mmd_curso) + "\n")
    caminhos["mapa_json"] = os.path.join(base, "mapa.json")
    with open(caminhos["mapa_json"], "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=1)
    caminhos["mmd_mapa"] = os.path.join(base, "mapa.mmd")
    with open(caminhos["mmd_mapa"], "w", encoding="utf-8") as f:
        f.write(mmd_mapa + "\n")
    caminhos["mmd_curso"] = os.path.join(base, "curso.mmd")
    with open(caminhos["mmd_curso"], "w", encoding="utf-8") as f:
        f.write(mmd_curso + "\n")
    diretorio_obsidian = os.path.join(base, "obsidian")
    motor_obsidian.gerar_vault(diretorio_obsidian, curso, mapa, mmd_mapa, mmd_curso)
    caminhos["obsidian"] = diretorio_obsidian
    return caminhos
