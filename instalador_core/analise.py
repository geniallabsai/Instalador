# -*- coding: utf-8 -*-
"""Análise estática leve: riscos COM evidência (arquivo:linha) e pontos fortes.
Heurística de propósito — cada risco vira, na Fase 5, uma pergunta do Cético.
Evidência é obrigatória: objeção sem endereço não entra no curso."""
import os
import re

_RISCOS = [
    ("critico", "credencial em claro",
     re.compile(r"(?i)\b(password|passwd|secret|senha|api[_-]?key|token)\b\s*[:=]\s*[\"'][^\"']{4,}[\"']")),
    ("critico", "chave reconhecível no código",
     re.compile(r"(ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[\w-]{8,})")),
    ("alto", "avaliação dinâmica (eval/exec)",
     re.compile(r"\b(eval|exec)\s*\(|os\.system\s*\(|new\s+Function\s*\(")),
    ("alto", "SQL montado por concatenação",
     re.compile(r"(?i)\b(execute|query|fetchone|fetchall|raw)\s*\(\s*f[\"']|[\"'](SELECT|INSERT|UPDATE|DELETE)\b[^\"']*[\"']\s*\+")),
    ("alto", "comando com shell=True", re.compile(r"shell\s*=\s*True")),
    ("alto", "HTML injetado direto", re.compile(r"innerHTML\s*=|document\.write\s*\(")),
    ("medio", "exceção ampla (risco de engolir erro)",
     re.compile(r"(?m)^\s*except\s*(Exception|BaseException)?\s*:")),
    ("medio", "CORS aberto", re.compile(r"(?i)origins?\s*[:=].*\*|\*\s*.*origin")),
    ("medio", "modo debug ligado", re.compile(r"(?m)^\s*DEBUG\s*=\s*True")),
    ("medio", "http sem TLS para fora", re.compile(r"http://(?!127\.0\.0\.1|localhost|0\.0\.0\.0)")),
    ("baixo", "pendência declarada", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")),
]

EXT_CODIGO = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".sh", ".bash",
              ".ps1", ".go", ".rs", ".java", ".c", ".cpp", ".cs", ".rb", ".php",
              ".swift", ".kt"}
MAX_RISCOS = 40


def detectar_riscos(arquivos, textos):
    """arquivos: metadados; textos: {caminho: texto}. → (riscos, estruturais)."""
    riscos, vistos = [], set()
    for a in arquivos:
        texto = textos.get(a["caminho"])
        if not texto:
            continue
        if os.path.splitext(a["caminho"])[1].lower() not in EXT_CODIGO:
            continue
        for nivel, titulo, rx in _RISCOS:
            for i, linha in enumerate(texto.splitlines(), 1):
                if rx.search(linha):
                    chave = (titulo, a["caminho"])
                    if chave in vistos:
                        break
                    vistos.add(chave)
                    riscos.append({"nivel": nivel, "titulo": titulo,
                                   "arquivo": a["caminho"], "linha": i,
                                   "trecho": linha.strip()[:110]})
                    break
    estruturais = []
    for a in arquivos:
        if a["linhas"] > 600:
            estruturais.append({"nivel": "medio", "arquivo": a["caminho"], "linha": "",
                                "texto": "arquivo com %d linhas: quem consegue revê-lo inteiro?" % a["linhas"]})
        for s in a.get("simbolos", []):
            if s["tipo"] == "funcao" and (s.get("fim") or 0) - s.get("linha", 0) > 60:
                estruturais.append({"nivel": "medio", "arquivo": a["caminho"], "linha": s["linha"],
                                    "texto": "função '%s' tem %d linhas: quantas responsabilidades escondidas?"
                                              % (s["nome"], s["fim"] - s["linha"])})
    return riscos[:MAX_RISCOS], estruturais[:8]


TESTE_RE = re.compile(r"(^|/)test_[^/]+\.py$|_test\.(py|js|ts)$|(^|/)tests?/")


def detectar_fortes(arquivos, cobertura_doc, com_hints, total_arquivos):
    fortes = []
    for a in arquivos:
        nome = a["caminho"]
        base = os.path.basename(nome)
        if TESTE_RE.search(nome) and base != "__init__.py":
            fortes.append({"titulo": "teste", "onde": nome})
            break
    nomes = {os.path.basename(a["caminho"]).lower() for a in arquivos}
    if any(n.startswith("dockerfile") for n in nomes):
        fortes.append({"titulo": "dockerfile", "onde": "Dockerfile"})
    if "license" in nomes or "license.md" in nomes:
        fortes.append({"titulo": "license", "onde": "LICENSE"})
    if any(n.startswith("readme") or n.startswith("leia-me") for n in nomes):
        fortes.append({"titulo": "readme", "onde": "README"})
    for a in arquivos:
        if a["caminho"].startswith(".github/workflows/"):
            fortes.append({"titulo": "ci", "onde": a["caminho"]})
            break
    if total_arquivos <= 40:
        fortes.append({"titulo": "pequeno", "onde": "projeto", "extra": total_arquivos})
    if cobertura_doc is not None and cobertura_doc >= 0.5:
        fortes.append({"titulo": "docstrings", "onde": "projeto",
                       "extra": int(round(cobertura_doc * 100))})
    if com_hints:
        fortes.append({"titulo": "type_hints", "onde": "projeto"})
    return fortes


def sugerir_leitura(arquivos):
    """Ordem sugerida: README → ponto de entrada → maiores."""
    ordem = []

    def _peso(a):
        base = os.path.basename(a["caminho"]).lower()
        if base.startswith("readme") or base.startswith("leia-me"):
            return 0
        if base in ("main.py", "app.py", "cli.py", "instalador", "index.js",
                    "index.ts", "main.go", "main.rs", "program.cs"):
            return 1
        return 2

    for a in sorted(arquivos, key=lambda x: (_peso(x), -x["linhas"])):
        ordem.append(a["caminho"])
        if len(ordem) >= 12:
            break
    return ordem
