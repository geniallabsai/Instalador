# -*- coding: utf-8 -*-
"""Escritor de PDF mínimo e honesto — stdlib pura, sem dependência.

A4 retrato, fontes base Helvetica / Helvetica-Bold / Helvetica-Oblique /
Courier, codificação WinAnsi (PT-BR completo), quebra de página automática,
blocos cinza para código, réguas e rodapé com numeração. Gera PDF 1.4 com
tabela xref validável — abre em qualquer leitor, para sempre."""

PAG_L = 595.0
PAG_A = 842.0
MARGEM = 56.0
MARGEM_SUP = 66.0
MARGEM_INF = 58.0
LARGURA_TEXTO = PAG_L - 2 * MARGEM

COR_TEXTO = (0.12, 0.14, 0.18)
COR_TITULO = (0.05, 0.18, 0.45)
COR_ACENTO = (0.76, 0.33, 0.04)
COR_CINZA = (0.42, 0.45, 0.50)
COR_CODIGO_FUNDO = (0.945, 0.952, 0.968)
COR_CODIGO_TXT = (0.13, 0.16, 0.22)
COR_VERDE = (0.10, 0.50, 0.28)
COR_VERMELHO = (0.78, 0.16, 0.12)
COR_AMBAR = (0.70, 0.50, 0.05)
COR_FAIXA = (0.90, 0.93, 0.98)


def _winansi(s):
    return s.encode("cp1252", errors="replace").decode("cp1252")


def _esc(s):
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


class _Pagina:
    __slots__ = ("itens",)

    def __init__(self):
        self.itens = []  # ("txt", x, y, fonte, tam, rgb, texto) | ("ret", x, y, w, h, rgb)


class Pdf:
    def __init__(self):
        self.paginas = [_Pagina()]
        self.y = PAG_A - MARGEM_SUP

    # ---------------- cursor / páginas ---------------- #

    @property
    def _pg(self):
        return self.paginas[-1]

    def _nova(self):
        self.paginas.append(_Pagina())
        self.y = PAG_A - MARGEM_SUP

    def quebra_pagina(self):
        self._nova()

    def _garante(self, altura):
        if self.y - altura < MARGEM_INF:
            self._nova()

    # ---------------- medição ---------------- #

    @staticmethod
    def _fator(fonte):
        return 0.60 if fonte == "F3" else 0.50

    def _largura(self, texto, fonte, tam):
        return len(_winansi(texto)) * tam * self._fator(fonte)

    def quebra(self, texto, fonte, tam, largura=LARGURA_TEXTO):
        palavras = _winansi(texto).split()
        if not palavras:
            return [""]
        linhas, atual = [], ""
        for p in palavras:
            if not p:
                continue
            if not atual:
                atual = p
                while self._largura(atual, fonte, tam) > largura and len(atual) > 1:
                    corte = max(2, int(len(atual) * (largura / self._largura(atual, fonte, tam))))
                    linhas.append(atual[:corte])
                    atual = atual[corte:]
                continue
            cand = atual + " " + p
            if self._largura(cand, fonte, tam) <= largura:
                atual = cand
            else:
                linhas.append(atual)
                while self._largura(p, fonte, tam) > largura and len(p) > 1:
                    corte = max(2, int(len(p) * (largura / self._largura(p, fonte, tam))))
                    linhas.append(p[:corte])
                    p = p[corte:]
                atual = p
        if atual:
            linhas.append(atual)
        return linhas

    # ---------------- primitivas ---------------- #

    def ret(self, x, y, w, h, rgb):
        self._pg.itens.append(("ret", x, y, w, h, rgb))

    def texto(self, texto, fonte="F1", tam=10, cor=COR_TEXTO, antes=0, depois=5,
              x=None, largura=None, alinh="esq", x_cont=None):
        x = MARGEM if x is None else x
        largura = LARGURA_TEXTO if largura is None else largura
        x_cont = x if x_cont is None else x_cont
        self._garante(antes + tam * 1.5)
        self.y -= antes
        if self.y < MARGEM_INF + tam:
            self._nova()
        entre = tam * 1.45
        for i, linha in enumerate(self.quebra(texto, fonte, tam, largura)):
            if not linha:
                self.y -= entre * 0.8
                continue
            self._garante(entre + tam)
            xx = x if i == 0 else x_cont
            if alinh == "dir":
                xx = x + largura - self._largura(linha, fonte, tam)
            self._pg.itens.append(("txt", xx, self.y, fonte, tam, cor, _winansi(linha)))
            self.y -= entre
        self.y -= depois

    def regua(self, espessura=1.1, cor=COR_ACENTO, antes=0):
        self._garante(espessura + antes)
        self.y -= antes
        self.rect_ = (MARGEM, self.y - 2, LARGURA_TEXTO, espessura)
        self.ret(MARGEM, self.y - 2, LARGURA_TEXTO, espessura, cor)
        self.y -= espessura + 8

    # ---------------- blocos compostos ---------------- #

    def h1(self, texto, cor=COR_TITULO):
        self.texto(texto, "F2", 15.5, cor, antes=6, depois=2)
        self.regua()

    def h2(self, texto):
        self.texto(texto, "F2", 12, (0.10, 0.26, 0.55), antes=10, depois=4)

    def lista(self, itens, fonte="F1", tam=10, cor=COR_TEXTO, marcador="•", extra=None):
        for i, it in enumerate(itens):
            cor_it = cor
            texto_it = it
            if extra:
                texto_it, cor_it = extra(i, it)
            self.texto(marcador + " " + texto_it, fonte, tam, cor_it, depois=2, x_cont=MARGEM + 13)

    def bloco_codigo(self, linhas, titulo=None, tam=8.6):
        entre = tam * 1.38
        maxch = int(LARGURA_TEXTO / (tam * 0.60))
        q = []
        for l in linhas:
            l = l.rstrip()
            while len(l) > maxch:
                q.append(l[:maxch])
                l = l[maxch:]
            q.append(l)
        titulo_h = 13.0 if titulo else 0.0
        h = titulo_h + len(q) * entre + 12
        self._garante(h + 8)
        self.y -= 6
        y_top = self.y
        self.ret(MARGEM - 5, y_top - h, LARGURA_TEXTO + 10, h, COR_CODIGO_FUNDO)
        cy = y_top - 6
        if titulo:
            self._pg.itens.append(("txt", MARGEM, cy, "F2", 7.6, COR_CINZA, _winansi(titulo.upper())))
            cy -= 12
        for l in q:
            cy -= entre
            self._pg.itens.append(("txt", MARGEM, cy, "F3", tam, COR_CODIGO_TXT, _winansi(l)))
        self.y = y_top - h - 8

    def nota(self, texto, autor=None):
        self._garante(24)
        self.y -= 4
        faixas = []
        entre = 12.5
        linhas = self.quebra(texto, "F4", 9.5, LARGURA_TEXTO - 26)
        h = len(linhas) * entre + (12 if autor else 0) + 14
        self.ret(MARGEM, self.y - h, 4.5, h, COR_ACENTO)
        self.ret(MARGEM + 4.5, self.y - h, LARGURA_TEXTO - 4.5, h, COR_FAIXA)
        cy = self.y - 14
        if autor:
            self._pg.itens.append(("txt", MARGEM + 14, cy, "F2", 8.5, COR_ACENTO, _winansi(autor.upper())))
            cy -= entre
        for l in linhas:
            self._pg.itens.append(("txt", MARGEM + 14, cy, "F4", 9.5, (0.25, 0.27, 0.32), _winansi(l)))
            cy -= entre
        self.y = self.y - h - 6

    # ---------------- serialização ---------------- #

    def _stream(self, pg):
        ops = []
        for it in pg.itens:
            if it[0] == "ret":
                _, x, y, w, h, rgb = it
                ops.append("%.3f %.3f %.3f rg" % rgb)
                ops.append("%.2f %.2f %.2f %.2f re f" % (x, y, w, h))
            else:
                _, x, y, fonte, tam, rgb, txt = it
                ops.append("BT")
                ops.append("/%s %.2f Tf" % (fonte, tam))
                ops.append("%.3f %.3f %.3f rg" % rgb)
                ops.append("1 0 0 1 %.2f %.2f Tm" % (x, y))
                ops.append("(%s) Tj" % _esc(_winansi(txt)))
                ops.append("ET")
        return "\n".join(ops).encode("cp1252", "replace")

    def salvar(self, caminho, rodape_esq="Genial Labs · INSTALADOR"):
        n = len(self.paginas)
        # rodapé a partir da página 2
        for idx in range(1, n):
            pg = self.paginas[idx]
            pg.itens.append(("ret", MARGEM, 44, LARGURA_TEXTO, 0.7, (0.80, 0.83, 0.88)))
            pg.itens.append(("txt", MARGEM, 32, "F1", 7.5, COR_CINZA, _winansi(rodape_esq)))
            direita = "pagina %d de %d" % (idx + 1, n)
            pg.itens.append(("txt", MARGEM + LARGURA_TEXTO - self._largura(direita, "F1", 7.5), 32, "F1", 7.5, COR_CINZA, _winansi(direita)))

        objetos = {}
        kids = []
        for i in range(n):
            kids.append("%d 0 R" % (7 + 2 * i))
        objetos[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
        objetos[2] = ("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join(kids), n)).encode("latin-1")
        objetos[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        objetos[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
        objetos[5] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"
        objetos[6] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>"
        for i in range(n):
            pag_num, con_num = 7 + 2 * i, 8 + 2 * i
            stream = self._stream(self.paginas[i])
            objetos[pag_num] = (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                "/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> >> "
                "/Contents %d 0 R >>" % con_num).encode("latin-1")
            objetos[con_num] = b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream)

        saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}
        for num in sorted(objetos):
            offsets[num] = len(saida)
            saida += ("%d 0 obj\n" % num).encode("latin-1")
            saida += objetos[num]
            saida += b"\nendobj\n"
        pos_xref = len(saida)
        total = max(objetos)
        saida += ("xref\n0 %d\n" % (total + 1)).encode("latin-1")
        saida += b"0000000000 65535 f \n"
        for num in range(1, total + 1):
            saida += ("%010d 00000 n \n" % offsets[num]).encode("latin-1")
        saida += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                  % (total + 1, pos_xref)).encode("latin-1")
        with open(caminho, "wb") as f:
            f.write(bytes(saida))
        return caminho

    def para_bytes(self, rodape_esq="Genial Labs · INSTALADOR"):
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            tmp = tf.name
        try:
            self.salvar(tmp, rodape_esq)
            with open(tmp, "rb") as f:
                return f.read()
        finally:
            os.unlink(tmp)
