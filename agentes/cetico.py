# -*- coding: utf-8 -*-
"""Cético — agente 3 de 6.

Ataca a explicação mais forte com evidência de arquivo:linha. Cada objeção
nasce com endereço; sem endereço, não entra no veredito. Três fontes, nessa
ordem: riscos detectados, riscos estruturais e perguntas universais. Se o
mapa ficar pobre em objeções factuais, pede ao modelo de IA (se houver)
até cinco novas, marcadas `modelo`. Máximo de dez no veredito.
"""

import json

from instalador_core import llm
from .comum import _fatos


class Cetico:
    nome = "Cético"
    papel = "desafia cada explicação: busca buraco, exceção e premissa oculta antes do aluno herdar a dúvida"

    FRASES = {
        "credencial em claro": "essa senha fica no código — quem mais já a viu? git blame não é cofre.",
        "chave reconhecível no código": "chave viva no repositório: rotação é rotina aqui ou é sorte?",
        "avaliação dinâmica (eval/exec)": "código escrevendo código em tempo de execução: o que acontece quando a string vem de fora?",
        "SQL montado por concatenação": "SQL por string: um traço na entrada vira injeção. Tem escape?",
        "comando com shell=True": "shell=True com dado variável: metacaractere no input vira comando?",
        "HTML injetado direto": "innerHTML com dado externo: XSS é consequência, não acidente.",
        "exceção ampla (risco de engolir erro)": "exceção que pode engolir: o erro some — quem descobre, e quando?",
        "CORS aberto": "CORS com estrela: qualquer site conversa com a API. Por quê?",
        "modo debug ligado": "DEBUG ligado vira vitrine de erro para o usuário.",
        "http sem TLS para fora": "http:// para fora: o pacote viaja de ônibus, não de mala diplomática.",
        "pendência declarada": "TODO no código é dívida assinada: alguém vai pagar?",
    }
    UNIVERSAIS = [
        "O que acontece quando a entrada vem vazia, gigante ou em outro idioma?",
        "E se dois processos rodarem isto ao mesmo tempo — algo compartilhado some em algum lugar?",
        "Quem valida o que vem de fora? Onde exatamente termina a confiança?",
        "Qual o caminho mais longo do usuário até este código — e onde ele quebra primeiro?",
    ]

    def objetar(self, mapa):
        objecoes = []
        for r in mapa.get("riscos", [])[:12]:
            frase = self.FRASES.get(r["titulo"], "por que isto aqui, exatamente?")
            objecoes.append({"nivel": r["nivel"],
                             "evidencia": "%s:%s" % (r["arquivo"], r["linha"]),
                             "texto": "%s (%s:%s)" % (frase, r["arquivo"], r["linha"])})
        for e in mapa.get("estruturais", [])[:4]:
            objecoes.append({"nivel": e["nivel"],
                             "evidencia": "%s:%s" % (e["arquivo"], e.get("linha", "")),
                             "texto": e["texto"]})
        if not any(f["titulo"] == "teste" for f in mapa.get("fortes", [])):
            objecoes.append({"nivel": "alto", "evidencia": "projeto",
                             "texto": "nenhum teste encontrado: o que garante que nada quebrou depois?"})
        cov = mapa.get("cobertura_doc")
        if cov is not None and cov < 0.5:
            objecoes.append({"nivel": "medio", "evidencia": "projeto",
                             "texto": "%.0f%% das funções sem docstring — o contrato vive na cabeça de quem escreveu."
                                       % (cov * 100)})
        for u in self.UNIVERSAIS:
            if len(objecoes) >= 8:
                break
            objecoes.append({"nivel": "baixo", "evidencia": "geral", "texto": u})
        objecoes = objecoes[:10]
        factuais = [o for o in objecoes if o["evidencia"] not in ("geral", "projeto")]
        if len(factuais) < 3:
            txt = llm.chamar(
                "Você é o Cético do Genial Labs: desconfiado, específico, educado. "
                "Responda SOMENTE com até 5 linhas iniciadas por '- ', cada uma uma objeção concreta sobre o material.",
                _fatos(mapa))
            if txt:
                linhas = [l.strip().lstrip("-• ").strip() for l in txt.splitlines()]
                linhas = [l for l in linhas if l][:5]
                if linhas:
                    objecoes = [{"nivel": "medio", "evidencia": "modelo", "texto": l} for l in linhas]
        return objecoes
