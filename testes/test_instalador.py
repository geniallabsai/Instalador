# -*- coding: utf-8 -*-
"""Suite do Instalador — offline (INSTALADOR_SEM_IA=1), stdlib pura."""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.dom.minidom
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["INSTALADOR_SEM_IA"] = "1"
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from instalador_core import arte, debaters, destripador, professor, relatorios  # noqa: E402
from instalador_core.socrates import Socrates, medir_nuance  # noqa: E402


def criar_projeto(tmp):
    """Mini-projeto com recursos conhecidos, para asserts deterministicos."""
    def w(rel, texto):
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(texto)

    w("README.md", "# Mini App\n\nAplicacao que converte unidades e guarda historico da sessao.\n\nFeita para a demo do Instalador.\n")
    w("LICENSE", "MIT License\nCopyright (c) 2026 Genial Labs AI\n")
    w("Dockerfile", "FROM python:3.13-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python3\", \"main.py\"]\n")
    w(".github/workflows/ci.yml", "name: ci\non: [push]\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: python3 -m unittest\n")
    w("config.json", '{"usuarios": [], "limite": 50, "debug": false}\n')
    w("main.py", r'''# -*- coding: utf-8 -*-
"""Mini App - ponto de entrada."""
import re
from utils import converter

CHAVE_API = "ghp_AbCdEfGhIjKlMnOpQrStUvWxYz012345"
DEBUG = True


def iniciar(args):
    """Inicia: recebe texto e devolve o resultado convertido."""
    partes = args.split()
    if len(partes) < 2:
        raise ValueError("uso: <origem> <valor>")
    return converter(partes[0], float(partes[1]))


def resumo(txt):
    """Extrai o primeiro numero do texto."""
    m = re.search(r"(\d+)", txt)
    return m.group(1) if m else ""
''')
    w("utils.py", r'''# -*- coding: utf-8 -*-
"""Conversoes utilitarias."""

TAXAS = {"km_mi": 0.621371, "c_f": 1.8}


def converter(origem, valor):
    """Converte pela tabela TAXAS."""
    taxa = TAXAS.get(origem)
    if taxa is None:
        raise KeyError(origem)
    return valor * taxa


def limpar(s):
    return s.strip().lower()
''')
    w("test_main.py", '''import unittest
from main import iniciar, resumo
from utils import converter


class T(unittest.TestCase):
    def test_iniciar(self):
        self.assertAlmostEqual(iniciar("km_mi 10"), 6.21371, places=4)

    def test_resumo(self):
        self.assertEqual(resumo("abc 7 xyz"), "7")

    def test_erro(self):
        self.assertRaises(KeyError, converter, "xx", 1)
''')
    w("notas.md", "# Notas\n\nDecisao: nao usar banco de dados por enquanto.\n\nMotivo: o projeto e pequeno.\n")
    return tmp


class TestArte(unittest.TestCase):
    def test_bloco_genial_labs(self):
        linhas = arte.bloco()
        self.assertEqual(len(linhas), 6)
        caixa = {chr(c) for c in range(0x2500, 0x25A0)}
        for l in linhas:
            self.assertTrue(l.strip(), "linha vazia")
            for c in l:
                self.assertIn(c, caixa | {" "}, repr(c))
        self.assertGreaterEqual(sum(l.count(chr(0x2588)) for l in linhas), 120)



class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="inst-teste-")
        cls.alvo = criar_projeto(cls.tmp)
        cls.mapa = destripador.Destripador().destruir(cls.alvo)
        cls.objecoes = debaters.Cetico().objetar(cls.mapa)
        cls.defesas = debaters.Convicto().defender(cls.mapa)
        cls.juizo = debaters.Juiz().decidir(cls.mapa, cls.objecoes, cls.defesas)
        cls.curso = professor.Professor().ensinar(cls.mapa, cls.juizo, sem_ia=True)
        cls.base = os.path.join(cls.tmp, "saida")
        cls.caminhos = relatorios.escrever_tudo(cls.base, cls.curso, cls.mapa)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # ---- agentes ------------------------------------------------- #

    def test_mapa(self):
        m = self.mapa
        self.assertEqual(m["arquivos_total"], 9)
        self.assertEqual(m["dominante"], "Python")
        main_riscos = [r for r in m["riscos"] if r["arquivo"] == "main.py"]
        self.assertTrue(any(r["nivel"] == "critico" for r in main_riscos))
        pares = [tuple(p) for p in m["grafo"]]
        self.assertIn(("main.py", "utils.py"), pares)
        self.assertIn(("test_main.py", "main.py"), pares)
        self.assertIn("main.py", m["leitura_sugerida"])
        titulos_fortes = {f["titulo"] for f in m["fortes"]}
        for esperado in ("teste", "dockerfile", "license", "readme", "ci", "pequeno"):
            self.assertIn(esperado, titulos_fortes)

    def test_debate(self):
        j = self.juizo
        self.assertTrue(5 <= j["confianca"] <= 99)
        self.assertEqual(len(j["barra"]), 20)
        self.assertEqual(set(j["pontuacao"]), {"pena", "ganho"})
        self.assertGreaterEqual(j["pontuacao"]["ganho"], 10)
        self.assertGreaterEqual(len(self.objecoes), 3)
        self.assertGreaterEqual(len(self.defesas), 5)
        for o in self.objecoes[:3]:
            self.assertIn("evidencia", o)
        self.assertTrue(j["resumo"])

    def test_socrates(self):
        alto = medir_nuance("essa funcao chama a API em um loop e grava no banco")
        baixo = medir_nuance("acho que e tipo assim, mais ou menos confuso pra mim")
        self.assertGreater(alto["nivel"], baixo["nivel"])
        soc = Socrates()
        estado = {"fase": 1, "nivel": 3, "seq": 0, "rodada": 0}
        q = soc.pergunta(self.mapa, estado)
        self.assertIsInstance(q, str)
        self.assertNotIn("{fn}", q)
        r = soc.responder(self.mapa, estado, "uma funcao que chama outra e devolve numero")
        self.assertGreater(len(r), 15)
        self.assertEqual(estado["rodada"], 1)

    def test_curso_estrutura(self):
        c = self.curso
        self.assertEqual(len(c["fases"]), 6)
        self.assertEqual([f["slug"] for f in c["fases"]],
                         ["visao-geral", "anatomia", "logica-principal",
                          "contratos-e-dados", "onde-quebra", "pratica"])
        for f in c["fases"]:
            self.assertTrue(f["blocos"], f["slug"])
            self.assertTrue(f["objetivo"])
        self.assertGreaterEqual(len(c["analogia"]), 30)
        self.assertEqual(len(c["prompts"]), 3)
        self.assertEqual(c["juizo"]["confianca"], self.juizo["confianca"])

    # ---- artefatos ------------------------------------------------ #

    def test_pdf_valido(self):
        dados = open(self.caminhos["pdf"], "rb").read()
        self.assertTrue(dados.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", dados.rstrip())
        self.assertIn(b"xref", dados)
        from pypdf import PdfReader
        leitor = PdfReader(io.BytesIO(dados))
        self.assertGreaterEqual(len(leitor.pages), 8)
        texto = "\n".join((p.extract_text() or "") for p in leitor.pages)
        self.assertIn("GENIAL LABS", texto)
        self.assertIn("Fase 1", texto)
        self.assertIn("Fase 6", texto)

    def test_docx_valido(self):
        dados = open(self.caminhos["docx"], "rb").read()
        z = zipfile.ZipFile(io.BytesIO(dados))
        nomes = z.namelist()
        self.assertIn("[Content_Types].xml", nomes)
        self.assertIn("word/document.xml", nomes)
        doc = z.read("word/document.xml").decode("utf-8")
        xml.dom.minidom.parseString(doc)
        self.assertIn("GENIAL LABS", doc)
        self.assertIn("Fase 1", doc)
        import docx
        documento = docx.Document(io.BytesIO(dados))
        self.assertGreater(len(documento.paragraphs), 30)

    def test_mermaid(self):
        m1 = open(self.caminhos["mmd_mapa"], encoding="utf-8").read()
        self.assertTrue(m1.startswith("flowchart TD"))
        self.assertIn("-->", m1)
        m2 = open(self.caminhos["mmd_curso"], encoding="utf-8").read()
        self.assertTrue(m2.startswith("flowchart TD"))
        for i in range(1, 7):
            self.assertIn("F%d" % i, m2)

    def test_obsidian_vault(self):
        d = self.caminhos["obsidian"]
        notas = sorted(os.listdir(d))
        self.assertEqual(len(notas), 9)
        bases = {n[:-3] for n in notas}
        for n in notas:
            t = open(os.path.join(d, n), encoding="utf-8").read()
            self.assertTrue(t.startswith("---"), n)
            sem_casas = re.sub(r"```.*?```", "", t, flags=re.S)
            alvos = set(re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", sem_casas))
            for a in alvos:
                self.assertIn(a.strip(), bases, "%s referencia [[%s]] inexistente" % (n, a))
        mapa_t = open(os.path.join(d, "mapa-estrutural.md"), encoding="utf-8").read()
        self.assertIn("```mermaid", mapa_t)
        moc = open(os.path.join(d, "00-moc.md"), encoding="utf-8").read()
        self.assertIn("[[veredito-do-juiz", moc)

    def test_markdown_agentes(self):
        t = open(self.caminhos["md"], encoding="utf-8").read()
        self.assertIn("<!-- instalador-curso", t)
        for i in range(1, 7):
            self.assertIn("## Fase %d \u2014 " % i, t)
        self.assertGreaterEqual(t.count("```mermaid"), 2)
        ini = t.rindex("```json")
        fim = t.index("```", ini + 7)
        indice = json.loads(t[ini + 7:fim])
        self.assertEqual(len(indice["fases"]), 6)
        self.assertIn("confianca", indice["juizo"])


class TestExemploCalculadora(unittest.TestCase):
    DIR = os.path.join(RAIZ, "exemplos", "calculadora")

    def _rodar(self, *args):
        return subprocess.run([sys.executable, os.path.join(self.DIR, "calculadora.py")] + list(args),
                              capture_output=True, text=True, env=dict(os.environ), timeout=60)

    def test_soma(self):
        r = self._rodar("+", "2", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("5", r.stdout)

    def test_expr(self):
        r = self._rodar("expr", "(2+3)*4")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("20", r.stdout)

    def test_divisao_por_zero(self):
        r = self._rodar("/", "1", "0")
        self.assertEqual(r.returncode, 1)


class TestCli(unittest.TestCase):
    def _rodar(self, *args, entrada=None, timeout=240):
        env = dict(os.environ)
        env["INSTALADOR_SEM_IA"] = "1"
        env["NO_COLOR"] = "1"
        return subprocess.run([sys.executable, os.path.join(RAIZ, "instalador")] + list(args),
                              input=entrada, capture_output=True, text=True, env=env, timeout=timeout)

    def test_arte_e_status(self):
        r = self._rodar("arte")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("\u2588", r.stdout)
        r2 = self._rodar("status")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        for agente in ("Destripador", "Professor", "C\u00e9tico", "Convicto", "Juiz", "S\u00f3crates"):
            self.assertIn(agente, r2.stdout)

    def test_destri(self):
        saida = tempfile.mkdtemp(prefix="inst-destri-")
        alvo = os.path.join(RAIZ, "exemplos", "calculadora")
        r = self._rodar("destri", alvo, "-o", saida)
        self.assertEqual(r.returncode, 0, r.stdout + "\n" + r.stderr)
        self.assertTrue(os.path.exists(os.path.join(saida, "mapa.json")))
        self.assertTrue(os.path.exists(os.path.join(saida, "mapa.mmd")))
        shutil.rmtree(saida, ignore_errors=True)

    def test_curso_completo(self):
        saida = tempfile.mkdtemp(prefix="inst-curso-")
        alvo = os.path.join(RAIZ, "exemplos", "calculadora")
        r = self._rodar("curso", alvo, "-o", saida)
        saida_txt = r.stdout + "\n" + r.stderr
        self.assertEqual(r.returncode, 0, saida_txt[-4000:])
        for f in ("curso.pdf", "curso.docx", "curso.md", "mapa.json", "mapa.mmd", "curso.mmd"):
            self.assertTrue(os.path.exists(os.path.join(saida, f)), f + " | " + saida_txt[-2500:])
        self.assertTrue(os.path.isdir(os.path.join(saida, "obsidian")))
        shutil.rmtree(saida, ignore_errors=True)

    def test_chat_pipeado(self):
        alvo = os.path.join(RAIZ, "exemplos", "calculadora")
        r = self._rodar("chat", alvo, "--rodadas", "3",
                        entrada="essa funcao faz um loop sobre a API e grava no banco\nsair\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("S\u00f3crates", r.stdout)


if __name__ == "__main__":
    unittest.main()
