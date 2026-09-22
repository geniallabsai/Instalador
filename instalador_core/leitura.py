# -*- coding: utf-8 -*-
"""Olhos do Destripador: lê qualquer arquivo ou pasta e extrai estrutura
básica (linguagem, símbolos, imports, títulos). Só stdlib."""
import json
import os
import re

PULAR_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", "venv", ".venv",
    "env", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", ".idea",
    ".vscode", "site-packages", ".obsidian", "target", "vendor", ".next",
}
MAX_ARQ = 2000
MAX_BYTES = 400_000

EXT_LINGUAGEM = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".ps1": "PowerShell",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".c": "C", ".h": "C",
    ".cpp": "C++", ".cc": "C++", ".cs": "C#", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala", ".lua": "Lua",
    ".md": "Markdown", ".rst": "RST", ".txt": "Texto",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
    ".ini": "INI", ".env": "ENV", ".csv": "CSV",
    ".html": "HTML", ".css": "CSS", ".scss": "CSS", ".sql": "SQL",
    ".vue": "Vue", ".svelte": "Svelte",
}
BINARIOS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg", ".pdf",
            ".zip", ".gz", ".tgz", ".tar", ".whl", ".pyc", ".woff", ".woff2",
            ".ttf", ".eot", ".otf", ".mp3", ".mp4", ".wav", ".avi", ".exe",
            ".dll", ".so", ".dylib", ".class", ".jar", ".wasm", ".sqlite", ".db"}


def linguagem_de(caminho):
    return EXT_LINGUAGEM.get(os.path.splitext(caminho)[1].lower(), "Outro")


def listar_arquivos(raiz):
    """Retorna caminhos relativos (separados por /) de tudo que dá para ler."""
    raiz_abs = os.path.abspath(raiz)
    if os.path.isfile(raiz_abs):
        return [os.path.basename(raiz_abs)]
    achados = []
    for dirpath, dirnames, filenames in os.walk(raiz_abs):
        dirnames[:] = [d for d in dirnames
                       if d not in PULAR_DIRS and (not d.startswith(".") or d == ".github")]
        for nome in sorted(filenames):
            ext = os.path.splitext(nome)[1].lower()
            if ext in BINARIOS:
                continue
            rel = os.path.relpath(os.path.join(dirpath, nome), raiz_abs).replace(os.sep, "/")
            achados.append(rel)
            if len(achados) >= MAX_ARQ:
                return achados
    return achados


def ler_texto(caminho, max_bytes=MAX_BYTES):
    try:
        with open(caminho, "rb") as f:
            bruto = f.read(max_bytes)
        return bruto.decode("utf-8", errors="replace")
    except OSError:
        return None


def _linha_em(texto, pos):
    return texto.count("\n", 0, pos) + 1


# ---------------- Python ----------------

def simbolos_python(texto):
    import ast
    simbolos, importa = [], []
    try:
        arvore = ast.parse(texto)
    except SyntaxError:
        return simbolos, importa

    def _doc(no):
        linhas = (ast.get_docstring(no) or "").strip().splitlines()
        return linhas[0][:140] if linhas else ""

    for no in ast.walk(arvore):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
            simbolos.append({
                "nome": no.name, "tipo": "funcao", "linha": no.lineno,
                "fim": getattr(no, "end_lineno", no.lineno), "doc": _doc(no),
                "args": [a.arg for a in no.args.args][:12],
            })
        elif isinstance(no, ast.ClassDef):
            metodos = [n.name for n in no.body
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            simbolos.append({
                "nome": no.name, "tipo": "classe", "linha": no.lineno,
                "fim": getattr(no, "end_lineno", no.lineno),
                "metodos": metodos[:24], "doc": _doc(no),
            })
    for no in arvore.body:
        if isinstance(no, ast.Import):
            for a in no.names:
                m = a.name.split(".")[0]
                if m and m not in importa:
                    importa.append(m)
        elif isinstance(no, ast.ImportFrom) and no.module:
            m = no.module.split(".")[0]
            if m and m not in importa:
                importa.append(m)
    return simbolos, importa


# ---------------- JavaScript / TypeScript ----------------

_RE_FUNC_JS = re.compile(r"(?:^|[^A-Za-z0-9_$])(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)")
_RE_SETA_JS = re.compile(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>")
_RE_CLASSE_JS = re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)")
_RE_IMPORTA_JS = re.compile(r"""from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\)""")


def simbolos_js(texto):
    simbolos, importa = [], []
    for m in _RE_CLASSE_JS.finditer(texto):
        simbolos.append({"nome": m.group(1), "tipo": "classe", "linha": _linha_em(texto, m.start()), "fim": 0, "doc": ""})
    for m in _RE_FUNC_JS.finditer(texto):
        simbolos.append({"nome": m.group(1), "tipo": "funcao", "linha": _linha_em(texto, m.start()), "fim": 0, "doc": ""})
    for m in _RE_SETA_JS.finditer(texto):
        if not any(s["nome"] == m.group(1) for s in simbolos):
            simbolos.append({"nome": m.group(1), "tipo": "funcao(seta)", "linha": _linha_em(texto, m.start()), "fim": 0, "doc": ""})
    for m in _RE_IMPORTA_JS.finditer(texto):
        origem = m.group(1) or m.group(2)
        top = origem.lstrip("./").split("/")[0].split(".")[0]
        if top and top not in importa:
            importa.append(top)
    return simbolos, importa


# ---------------- Shell ----------------

_RE_FUNC_SH = re.compile(r"(?:^|\n)\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)\s*\{")


def simbolos_shell(texto):
    simbolos = []
    if texto.startswith("#!") and texto.splitlines():
        simbolos.append({"nome": "shebang", "tipo": "entrada", "linha": 1, "fim": 1,
                         "doc": texto.splitlines()[0][2:].strip()[:100]})
    for m in _RE_FUNC_SH.finditer(texto):
        simbolos.append({"nome": m.group(1), "tipo": "funcao(shell)",
                         "linha": _linha_em(texto, m.start()), "fim": 0, "doc": ""})
    return simbolos, []


# ---------------- Markdown / dados ----------------

_RE_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.M)
_RE_CHAVE_TOP = re.compile(r"^([A-Za-z_][\w.-]*)\s*:", re.M)


def simbolos_markdown(texto):
    simbolos = []
    for m in _RE_HEADING.finditer(texto):
        nivel = len(m.group(1))
        titulo = m.group(2).strip()[:100]
        simbolos.append({"nome": titulo, "tipo": "secao(%d)" % nivel,
                         "linha": _linha_em(texto, m.start()), "fim": 0, "doc": ""})
    return simbolos[:60], []


def simbolos_dados(texto):
    chaves = []
    try:
        d = json.loads(texto)
        if isinstance(d, dict):
            chaves = list(d.keys())[:30]
    except ValueError:
        for m in _RE_CHAVE_TOP.finditer(texto):
            chaves.append(m.group(1))
            if len(chaves) >= 30:
                break
    return [{"nome": c, "tipo": "chave/topo", "linha": 0, "fim": 0, "doc": ""} for c in chaves], []


EXTRATORES = {
    "Python": lambda t: simbolos_python(t),
    "JavaScript": lambda t: simbolos_js(t),
    "TypeScript": lambda t: simbolos_js(t),
    "Vue": lambda t: simbolos_js(t),
    "Svelte": lambda t: simbolos_js(t),
    "Shell": lambda t: simbolos_shell(t),
    "PowerShell": lambda t: ([], []),
    "Markdown": lambda t: simbolos_markdown(t),
    "RST": lambda t: simbolos_markdown(t),
    "JSON": lambda t: simbolos_dados(t),
    "YAML": lambda t: simbolos_dados(t),
    "TOML": lambda t: simbolos_dados(t),
    "INI": lambda t: ([], []),
}


def extrair(caminho, texto, linguagem):
    f = EXTRATORES.get(linguagem)
    if not f:
        return [], []
    return f(texto)
