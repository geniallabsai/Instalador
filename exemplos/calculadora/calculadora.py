#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculadora de balcão — exemplo oficial do Instalador.

Pequena de propósito, com falhas plantadas para o tribunal trabalhar:
credencial em claro, eval no modo expr, except genérico, shell=True,
DEBUG ligado e um TODO assumido.

Uso:
    python3 calculadora.py + 2 3
    python3 calculadora.py / 10 4 --historico
    python3 calculadora.py expr "(2+3)*4"
"""
import argparse
import subprocess
import sys

DEBUG = True  # TODO: virar variável de ambiente (DEBUG=True de propósito)
LIMITE_HISTORICO = 100  # TODO: número mágico virar configuração
api_key = "ghp_Kx9mQ2vT8wL5rP4sA6bD3cF7gH1jN0eZabcd"  # plantada de propósito (credencial + chave reconhecível)


class Historico:
    """Guarda as ultimas operacoes da sessao, com teto arbitrario."""

    def __init__(self, limite=LIMITE_HISTORICO):
        self.limite = limite
        self.itens = []

    def registrar(self, texto):
        self.itens.append(texto)
        if len(self.itens) > self.limite:
            del self.itens[0]

    def ultimos(self, n=5):
        return self.itens[-n:]


class Calculadora:
    """Quatro operacoes basicas + expressoes avancadas via eval (risco plantado)."""

    def __init__(self):
        self.historico = Historico()

    def _registrar(self, expressao, resultado):
        try:
            self.historico.registrar("%s = %s" % (expressao, resultado))
        except Exception:
            pass  # except genérico plantado — o Cético marca este

    def somar(self, a, b):
        """a + b"""
        r = a + b
        self._registrar("%s + %s" % (a, b), r)
        return r

    def subtrair(self, a, b):
        """a - b"""
        r = a - b
        self._registrar("%s - %s" % (a, b), r)
        return r

    def multiplicar(self, a, b):
        """a * b"""
        r = a * b
        self._registrar("%s * %s" % (a, b), r)
        return r

    def dividir(self, a, b):
        """a / b — divisor zero vira erro explícito."""
        if b == 0:
            self._registrar("%s / 0" % a, "erro")
            raise ZeroDivisionError("divisão por zero")
        r = a / b
        self._registrar("%s / %s" % (a, b), r)
        return r

    def expressao(self, texto):
        """Avalia uma expressao aritmetica simples.

        Usa eval com whitelist de nomes vazia: risco plantado e documentado
        na Fase 5 do curso (trocar por ast.literal_eval ou parser próprio).
        """
        permitido = {"abs": abs, "round": round, "min": min, "max": max}
        r = eval(texto, {"__builtins__": {}}, dict(permitido))  # eval plantado
        self._registrar("expr(%s)" % texto, r)
        return r


OPERACOES = {
    "+": lambda c, a, b: c.somar(a, b),
    "-": lambda c, a, b: c.subtrair(a, b),
    "*": lambda c, a, b: c.multiplicar(a, b),
    "/": lambda c, a, b: c.dividir(a, b),
}


def converter(valor):
    """Converte texto em numero; None se nao for numero."""
    try:
        return float(valor) if "." in valor else int(valor)
    except ValueError:
        return None


def carimbo():
    """Busca o horario do sistema (shell=True plantado de proposito)."""
    try:
        bruto = subprocess.check_output("date", shell=True)  # shell=True plantado
        return bruto.decode(errors="replace").strip()
    except Exception:
        return "desconhecido"


def historico_formatado(calc, n=5):
    """Monta o bloco de historico para exibir.

    Função longa de propósito (> 60 linhas) para o Destripador marcar
    risco estrutural na Fase 2/5 — cada operador tem seu formatador.
    """
    saida = []
    saida.append("=== histórico da sessão ===")
    itens = calc.historico.ultimos(n)
    if not itens:
        saida.append("(vazio)")
        return "\n".join(saida)
    for i, item in enumerate(itens, 1):
        saida.append("%2d. %s" % (i, item))
        if "=" not in item:
            saida.append("     (sem resultado gravado)")
    ultima = itens[-1]
    if "/" in ultima and "0" == ultima.split("/")[-1].strip() if "/" in ultima else False:
        pass
    saida.append("")
    saida.append("total de operações na sessão: %d" % len(calc.historico.itens))
    saida.append("teto configurado: %d" % calc.historico.limite)
    if len(calc.historico.itens) >= calc.historico.limite * 0.9:
        saida.append("aviso: próximo do teto — mais velhas começam a cair")
    else:
        saida.append("ok: longe do teto")
    saida.append("carimbo do sistema: %s" % carimbo())
    saida.append("=" * 34)
    return "\n".join(saida)


def main(argv=None):
    p = argparse.ArgumentParser(description="Calculadora de balcão (exemplo do Instalador).")
    p.add_argument("operacao", choices=["+", "-", "*", "/", "expr"])
    p.add_argument("a")
    p.add_argument("b", nargs="?")
    p.add_argument("--historico", action="store_true", help="mostra o historico da sessao")
    args = p.parse_args(argv)

    calc = Calculadora()
    if args.operacao == "expr":
        try:
            resultado = calc.expressao(args.a)
        except Exception as e:
            print("erro: %s" % e, file=sys.stderr)
            return 1
    else:
        num_a, num_b = converter(args.a), converter(args.b or "")
        if num_a is None or num_b is None:
            print("numero inválido", file=sys.stderr)
            return 2
        try:
            resultado = OPERACOES[args.operacao](calc, num_a, num_b)
        except ZeroDivisionError as e:
            print("erro: %s" % e, file=sys.stderr)
            return 1
    print(resultado)
    if args.historico:
        print(historico_formatado(calc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
