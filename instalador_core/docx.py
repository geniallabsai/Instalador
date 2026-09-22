# -*- coding: utf-8 -*-
"""Escritor de DOCX mínimo e honesto — stdlib pura (zipfile + XML).

OOXML de verdade: abre no Word, LibreOffice e WPS sem plugin, editável.
Sem estilos.xml (formatação inline via rPr), tabelas com borda, código
com sombra, quebra de página. Compatível com python-docx para validação."""
import zipfile
from xml.sax.saxutils import escape

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

COR_TEXTO = "1F2430"
COR_TITULO = "0E2E73"
COR_H2 = "1B4189"
COR_CINZA = "6B7280"
COR_CODIGO_FUNDO = "F1F3F8"
COR_FAIXA = "FDF3E7"


def _rpr(fonte=None, b=False, i=False, tam=None, cor=None):
    s = "<w:rPr>"
    if fonte:
        s += '<w:rFonts w:ascii="%s" w:hAnsi="%s"/>' % (fonte, fonte)
    if b:
        s += "<w:b/>"
    if i:
        s += "<w:i/>"
    if cor:
        s += '<w:color w:val="%s"/>' % cor
    if tam:  # em meio-pontos
        s += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (tam, tam)
    s += "</w:rPr>"
    return s


def _run(texto, **kw):
    return "<w:r>%s<w:t xml:space=\"preserve\">%s</w:t></w:r>" % (_rpr(**kw), escape(texto))


def _par(rodas, antes=0, depois=120, shd=None, keep_next=False):
    ppr = "<w:pPr>"
    ppr += '<w:spacing w:before="%d" w:after="%d" w:line="264" w:lineRule="auto"/>' % (antes, depois)
    if keep_next:
        ppr += "<w:keepNext/>"
    if shd:
        ppr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shd
    ppr += "</w:pPr>"
    return "<w:p>%s%s</w:p>" % (ppr, "".join(rodas))


class Docx:
    def __init__(self):
        self.body = []

    # ---------------- blocos ---------------- #

    def texto(self, texto, tam=22, cor=COR_TEXTO, b=False, i=False, fonte=None, antes=0, depois=140):
        self.body.append(_par([_run(texto, tam=tam, cor=cor, b=b, i=i, fonte=fonte)], antes=antes, depois=depois))

    def h1(self, texto):
        self.body.append(_par([_run(texto, tam=31, cor=COR_TITULO, b=True)], antes=240, depois=60, keep_next=True))
        self.body.append(_par([_run("", tam=8)], antes=0, depois=140, shd="D9E1F2"))

    def h2(self, texto):
        self.body.append(_par([_run(texto, tam=25, cor=COR_H2, b=True)], antes=240, depois=100, keep_next=True))

    def lista(self, itens, marcador="•", tam=22, cor=COR_TEXTO):
        for it in itens:
            self.body.append(_par([_run(marcador + "  " + it, tam=tam, cor=cor)], antes=0, depois=60))

    def bloco_codigo(self, linhas, titulo=None, tam=17):
        if titulo:
            self.body.append(_par([_run(titulo.upper(), tam=15, cor=COR_CINZA, b=True)], antes=120, depois=40))
        for l in linhas:
            self.body.append(_par([_run(l if l else " ", fonte="Courier New", tam=tam, cor="2A3140")], antes=0, depois=0, shd=COR_CODIGO_FUNDO))
        self.body.append(_par([_run(" ", tam=8)], antes=0, depois=80))

    def nota(self, texto, autor=None):
        rodas = []
        if autor:
            rodas.append(_run(autor.upper() + "   ", tam=16, cor="B45309", b=True))
        rodas.append(_run(texto, tam=19, i=True, cor="3F4552"))
        self.body.append(_par(rodas, antes=140, depois=160, shd=COR_FAIXA))

    def tabela(self, cab, linhas, tam=18):
        xml = ['<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>',
               '<w:tblBorders>' + "".join(
                   '<w:%s w:val="single" w:sz="4" w:space="0" w:color="C9CFDA"/>' % b
                   for b in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>",
               "</w:tblPr><w:tblGrid>"]
        for _ in cab:
            xml.append("<w:gridCol/>")
        xml.append("</w:tblGrid>")
        xml.append("<w:tr>")
        for c in cab:
            xml.append('<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/><w:shd w:val="clear" w:fill="%s"/></w:tcPr>%s</w:tc>'
                       % ("E4EAF5", _par([_run(c, tam=tam, b=True, cor=COR_TITULO)], depois=0)))
        xml.append("</w:tr>")
        for linha in linhas:
            xml.append("<w:tr>")
            for c in linha:
                xml.append('<w:tc><w:tcPr><w:tcW w:w="0" w:type="auto"/></w:tcPr>%s</w:tc>'
                           % _par([_run(str(c), tam=tam, cor=COR_TEXTO)], depois=0))
            xml.append("</w:tr>")
        xml.append("</w:tbl>")
        self.body.append("".join(xml))
        self.body.append(_par([_run(" ", tam=8)], antes=0, depois=60))

    def quebra_pagina(self):
        self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    # ---------------- serialização ---------------- #

    def _document(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="%s">'
                '<w:body>%s'
                '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
                'w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
                '</w:body></w:document>' % (NS_W, "".join(self.body)))

    CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                     '</Types>')
    RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')

    def para_bytes(self):
        zio = __import__("io").BytesIO()
        with zipfile.ZipFile(zio, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", self.CONTENT_TYPES.encode("utf-8"))
            z.writestr("_rels/.rels", self.RELS.encode("utf-8"))
            z.writestr("word/document.xml", self._document().encode("utf-8"))
        return zio.getvalue()

    def salvar(self, caminho):
        dados = self.para_bytes()
        with open(caminho, "wb") as f:
            f.write(dados)
        return caminho
