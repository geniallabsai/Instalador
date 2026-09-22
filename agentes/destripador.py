# -*- coding: utf-8 -*-
"""Destripador — o primeiro agente da cadeia. Lê o alvo inteiro e devolve o
mapa estrutural: a matéria-prima que os outros agentes usam para falar com verdade."""
import datetime
import os
import re

from instalador_core import analise, leitura


class Destripador:
    nome = "Destripador"
    papel = "destrincha qualquer código, programa ou pasta e produz o mapa estrutural com evidências"

    def destruir(self, alvo, ao_avisar=None):
        alvo = os.path.abspath(alvo)
        if ao_avisar:
            ao_avisar("localizando arquivos…", 0, 0)
        caminhos = leitura.listar_arquivos(alvo)
        arquivos, linguagens, textos = [], {}, {}
        total_linhas = 0
        for i, rel in enumerate(caminhos):
            if ao_avisar:
                ao_avisar("lendo arquivos", i + 1, len(caminhos))
            texto = leitura.ler_texto(os.path.join(alvo, rel))
            if texto is None:
                continue
            lang = leitura.linguagem_de(rel)
            linguagens[lang] = linguagens.get(lang, 0) + 1
            linhas = texto.count("\n") + 1
            total_linhas += linhas
            simbolos, imports = leitura.extrair(rel, texto, lang)
            meta = {"caminho": rel, "linhas": linhas, "linguagem": lang,
                    "simbolos": simbolos[:80], "imports": imports[:40]}
            if lang == "Python" and simbolos:
                funs = [s for s in simbolos if s["tipo"] == "funcao"]
                docs = [s for s in funs if s.get("doc")]
                meta["stats"] = {"defs": len(funs), "com_doc": len(docs),
                                 "hints": bool(re.search(r"(?m)^\s*def\s+\w+\([^)]*\)\s*->", texto))}
            arquivos.append(meta)
            if len(textos) < 300:
                textos[rel] = texto
        if ao_avisar:
            ao_avisar("conectando dependências e caçando riscos", 1, 1)
        grafo = self._grafo_local(arquivos)
        riscos, estruturais = analise.detectar_riscos(arquivos, textos)
        cov, hints = self._cobertura(arquivos)
        fortes = analise.detectar_fortes(arquivos, cov, hints, len(arquivos))
        return {
            "nome": os.path.basename(alvo.rstrip(os.sep)) or alvo,
            "raiz": alvo,
            "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
            "arquivos_total": len(arquivos),
            "linhas_total": total_linhas,
            "linguagens": dict(sorted(linguagens.items(), key=lambda kv: -kv[1])),
            "dominante": (max(linguagens, key=lambda k: linguagens[k]) if linguagens else None),
            "resumo": self._resumo(alvo, arquivos),
            "arquivos": arquivos,
            "grafo": grafo,
            "riscos": riscos,
            "estruturais": estruturais,
            "fortes": fortes,
            "cobertura_doc": cov,
            "leitura_sugerida": analise.sugerir_leitura(arquivos),
        }

    @staticmethod
    def _cobertura(arquivos):
        defs = docs = 0
        hints = False
        for a in arquivos:
            st = a.get("stats")
            if st:
                defs += st["defs"]
                docs += st["com_doc"]
                hints = hints or bool(st.get("hints"))
        return (docs / float(defs) if defs else None), hints

    @staticmethod
    def _grafo_local(arquivos):
        conjunto = {a["caminho"] for a in arquivos}
        stems = {}
        for a in arquivos:
            base = os.path.splitext(os.path.basename(a["caminho"]))[0].lower()
            stems.setdefault(base, a["caminho"])
        grafo, vistos = [], set()
        sufixos = ("", ".js", ".jsx", ".ts", ".tsx", ".py")
        for a in arquivos:
            diretorio = os.path.dirname(a["caminho"])
            for imp in a["imports"]:
                destino = None
                if imp.startswith((".", "/")):
                    base_dir = os.path.normpath(os.path.join(diretorio, imp)).replace(os.sep, "/")
                    candids = [base_dir + s for s in sufixos] + [base_dir + "/index.js", base_dir + "/index.ts"]
                    for cand in candids:
                        if cand in conjunto:
                            destino = cand
                            break
                else:
                    cabeca = imp.split("/")[0].split(".")[0].lower()
                    if cabeca in stems:
                        destino = stems[cabeca]
                if destino and destino != a["caminho"]:
                    par = (a["caminho"], destino)
                    if par not in vistos:
                        vistos.add(par)
                        grafo.append(list(par))
        return grafo[:200]

    @staticmethod
    def _resumo(alvo, arquivos):
        readme = None
        for a in arquivos:
            base = os.path.basename(a["caminho"]).lower()
            if (base.startswith("readme") or base.startswith("leia-me")) and os.path.dirname(a["caminho"]) == "":
                readme = a["caminho"]
                break
        if readme is None:
            for a in arquivos:
                if os.path.splitext(a["caminho"])[1].lower() in (".md", ".rst") and os.path.dirname(a["caminho"]) == "":
                    readme = a["caminho"]
                    break
        texto = ""
        if readme:
            try:
                with open(os.path.join(alvo, readme), "rb") as f:
                    texto = f.read(20000).decode("utf-8", errors="replace")
            except OSError:
                texto = ""
        for par in texto.split("\n\n"):
            limpo = " ".join(par.split())
            limpo = re.sub(r"[#>*`\-\|]", "", limpo).strip()
            if len(limpo) >= 40 and not limpo.lower().startswith(("http", "![", "[//", "badge")):
                return limpo[:400]
        cont = {}
        for a in arquivos:
            cont[a["linguagem"]] = cont.get(a["linguagem"], 0) + 1
        dom = max(cont.items(), key=lambda kv: kv[1])[0] if cont else "?"
        return "Projeto com %d arquivos; linguagem dominante: %s." % (len(arquivos), dom)
