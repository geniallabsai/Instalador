# -*- coding: utf-8 -*-
"""Sócrates: nunca entrega a resposta. Mede a nuance de quem responde
(jargão, hesitação, extensão) e recalibra a próxima pergunta. É ele quem faz
o terminal ter conversação — e quem interroga os outros agentes."""

TECNICO = ["função", "funcao", "variável", "variavel", "api", "endpoint", "banco", "loop",
           "recurs", "classe", "módulo", "modulo", "estado", "cache", "async", "assíncron",
           "parser", "json", "regex", "thread", "processo", "socket", "hash", "stack", "heap",
           "deploy", "commit", "branch", "mock", "contrato", "interface", "árvore", "arvore",
           "grafo", "funcao(", "dependênc", "dependenc"]
HESITA = ["acho", "tipo assim", "mais ou menos", "não sei", "naum", "confuso", "difícil",
          "dificil", "talvez", "será que", "sera que", "quase que", "unsim", "tá confuso"]


def medir_nuance(texto):
    """Mede o interlocutor: nível 1–5, tom e sinais que justificam a calibração."""
    t = (texto or "").lower().strip()
    if not t:
        return {"nivel": 2, "tom": "silêncio", "sinais": []}
    sinais = [w for w in TECNICO if w in t]
    hesita = [w for w in HESITA if w in t]
    pont = min(3, len(sinais)) + (1 if len(t) > 140 else 0) - (1 if hesita else 0)
    nivel = max(1, min(5, 3 + pont))
    tom = "hesitante" if hesita else ("técnica" if len(sinais) >= 2 else "casual")
    return {"nivel": nivel, "tom": tom, "sinais": (sinais + hesita)[:8]}


BANCO = {
    1: [(1, "Se isto fosse uma pessoa na sua rua, qual seria o ofício dela?"),
        (3, "O resumo diz: \"{doc}\". Qual problema real do mundo isso resolve — e quem sente a dor quando quebra?")],
    2: [(1, "Sem abrir nenhum arquivo: quantas peças principais você imagina, e por quê?"),
        (3, "Olhando {arq}: qual o trabalho dele dentro da casa — e quem ele chama quando precisa?"),
        (5, "Se você pudesse apagar UM arquivo sem quebrar o essencial, qual seria? Justifique com o grafo.")],
    3: [(1, "Quando o programa começa a rodar, qual a PRIMEIRA coisa que acontece?"),
        (4, "Seguindo {fn} passo a passo: onde mora a decisão que divide o mundo em caminhos?"),
        (5, "Qual estado muda entre uma chamada e outra de {fn}? Se não houver, por quê?")],
    4: [(2, "{fn} recebe {args} — o que acontece se chegar vazio? enorme? do tipo errado?"),
        (4, "O formato trocado entre as peças é um contrato. Quem quebra esse contrato paga o quê?")],
    5: [(1, "O Cético afirmou: “{obj}”. Concorda? Mostre onde a objeção quebra — ou onde ela acerta."),
        (4, "Se você tivesse que causar o pior defeito deste sistema em 30 segundos, por onde começaria?")],
    6: [(1, "Explique {fn} em voz alta para uma criança de 10 anos. Nenhuma palavra técnica."),
        (3, "Mude UMA escolha do autor em {arq}. Qual mudança? Que barulho ela faz no resto?")],
}


class Socrates:
    nome = "Sócrates"
    papel = "faz perguntas para o aluno e para os outros agentes; a resposta nunca sai pronta"

    def contexto(self, mapa):
        ctx = {"fn": "a função principal", "arq": "o ponto de entrada",
               "args": "seus parâmetros", "obj": "a objeção mais dura do Cético",
               "doc": (mapa.get("resumo") or "projeto analisado")[:160]}
        if not mapa:
            return ctx
        for a in sorted(mapa.get("arquivos", []), key=lambda x: -x["linhas"]):
            for s in a.get("simbolos", []):
                if s["tipo"] == "funcao":
                    ctx["fn"] = s["nome"]
                    ctx["arq"] = a["caminho"]
                    if s.get("doc"):
                        ctx["doc"] = s["doc"]
                    break
            if ctx["fn"] != "a função principal":
                break
        riscos = mapa.get("riscos") or []
        if riscos:
            r = riscos[0]
            ctx["obj"] = "%s — %s:%s" % (r["titulo"], r["arquivo"], r["linha"])
        return ctx

    @staticmethod
    def _preencher(template, ctx):
        try:
            return template.format(**ctx)
        except (KeyError, IndexError, ValueError):
            return template

    def pergunta(self, mapa, estado):
        fase = max(1, min(6, int(estado.get("fase", 1))))
        nivel = max(1, min(5, int(estado.get("nivel", 3))))
        opcoes = [t for minimo, t in BANCO[fase] if minimo <= nivel] or [t for _, t in BANCO[fase]]
        seq = int(estado.get("seq", 0))
        estado["seq"] = seq + 1
        return self._preencher(opcoes[seq % len(opcoes)], self.contexto(mapa))

    def responder(self, mapa, estado, resposta):
        nuance = medir_nuance(resposta)
        nivel_ant = int(estado.get("nivel", 3))
        estado["nivel"] = nuance["nivel"]
        estado["rodada"] = int(estado.get("rodada", 0)) + 1
        vistos = estado.setdefault("sinais_vistos", [])
        for s in nuance["sinais"]:
            if s not in vistos:
                vistos.append(s)
        mov = nuance["nivel"] - nivel_ant
        if mov > 0:
            calib = "Você trouxe substância — subindo para o nível %d." % nuance["nivel"]
        elif mov < 0:
            calib = "Sem pressa: reformulo menor, nível %d." % nuance["nivel"]
        else:
            calib = "Nível mantido (%d). Vamos mais fundo no mesmo ponto." % nuance["nivel"]
        eco = (resposta or "").strip().split("\n")[0][:80]
        base = 'Você disse: "%s…". ' % eco if eco else ""
        return base + calib + " " + self.pergunta(mapa, estado)
