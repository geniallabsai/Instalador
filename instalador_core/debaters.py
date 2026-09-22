# -*- coding: utf-8 -*-
"""Os três que fazem o curso não ser papo furado:
Cético (ataca com evidência), Convicto (defende com evidência), Juiz (decide
com pontuação explícita). O material só vira ensino depois de passar por aqui."""
import json

from . import llm


def _fatos(mapa, limite=1800):
    trecho = {
        "nome": mapa.get("nome"),
        "resumo": (mapa.get("resumo") or "")[:240],
        "linguagens": mapa.get("linguagens"),
        "arquivos_total": mapa.get("arquivos_total"),
        "linhas_total": mapa.get("linhas_total"),
        "top": [a["caminho"] for a in sorted(mapa.get("arquivos", []), key=lambda x: -x["linhas"])[:10]],
        "riscos": mapa.get("riscos", [])[:6],
        "fortes": [f["titulo"] for f in mapa.get("fortes", [])],
    }
    return json.dumps(trecho, ensure_ascii=False)[:limite]


NIVEL_PENTO = {"critico": 8, "alto": 5, "medio": 2, "baixo": 1}


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


class Convicto:
    nome = "Convicto"
    papel = "defende o material com a versão mais forte da explicação, sempre apontando evidência"

    def defender(self, mapa):
        defesas = []
        for f in mapa.get("fortes", []):
            t = f["titulo"]
            onde = f.get("onde", "projeto")
            if t == "teste":
                defesas.append({"texto": "existe teste no projeto — regressão tem rede de proteção", "evidencia": onde})
            elif t == "ci":
                defesas.append({"texto": "pipeline de CI ativo: nada entra sem passar pelos gates", "evidencia": onde})
            elif t == "dockerfile":
                defesas.append({"texto": "Dockerfile presente: ambiente reproduzível, fim do 'mas na minha máquina...'", "evidencia": onde})
            elif t == "license":
                defesas.append({"texto": "licença publicada: uso e derivação têm regra", "evidencia": onde})
            elif t == "readme":
                defesas.append({"texto": "README explica o propósito: o projeto nasce documentado", "evidencia": onde})
            elif t == "docstrings":
                defesas.append({"texto": "%.0f%% das funções documentam o próprio contrato" % f.get("extra", 0), "evidencia": onde})
            elif t == "type_hints":
                defesas.append({"texto": "type hints presentes: o contrato fala dentro do código", "evidencia": onde})
            elif t == "pequeno":
                defesas.append({"texto": "superfície pequena: %d arquivos — dá para ler tudo antes de confiar" % f.get("extra", 0),
                                "evidencia": onde})
        if not defesas:
            defesas.append({"texto": "o mapa estrutural existe e é verificável arquivo a arquivo — cada afirmação deste curso aponta para o código",
                            "evidencia": "mapa.json"})
        txt = llm.chamar(
            "Você é o Convicto do Genial Labs: sustenta o material com a versão mais forte da explicação, "
            "sempre com evidência. Responda SOMENTE com até 3 linhas iniciadas por '- '.",
            _fatos(mapa))
        if txt:
            linhas = [l.strip().lstrip("-• ").strip() for l in txt.splitlines()]
            linhas = [l for l in linhas if l][:3]
            defesas.extend({"texto": l, "evidencia": "modelo"} for l in linhas)
        return defesas[:8]


class Juiz:
    nome = "Juiz"
    papel = "arbitra Cético × Convicto: pontua, mede a confiança e redige o veredito"

    def decidir(self, mapa, objecoes, defesas):
        pena = sum(NIVEL_PENTO.get(o.get("nivel", "baixo"), 1) for o in objecoes)
        ganho = min(10, 2 * len(defesas))
        confianca = max(5, min(99, 90 - pena + ganho))
        if confianca >= 80:
            decisao = "material sólido — explicar como está, citando as ressalvas"
        elif confianca >= 55:
            decisao = "aceito com ressalvas — ensinar primeiro as objeções marcadas, depois o mérito"
        else:
            decisao = "questionado — o aluno precisa ver onde quebra ANTES de aprender o caminho feliz"
        cheio = int(round(confianca / 5.0))
        barra = "█" * cheio + "░" * (20 - cheio)
        resumo = ("O Cético apresentou %d objeções (pena %d); o Convicto sustentou %d defesas (ganho %d). "
                  "Confiança final: %d/100. Veredito: %s.") % (
                      len(objecoes), pena, len(defesas), ganho, confianca, decisao)
        return {"confianca": confianca, "decisao": decisao, "barra": barra,
                "pontuacao": {"pena": pena, "ganho": ganho}, "resumo": resumo,
                "objecoes": objecoes, "defesas": defesas}
