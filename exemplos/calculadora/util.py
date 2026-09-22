# -*- coding: utf-8 -*-
"""Apoio da calculadora: busca no histórico simulada com SQL montada por string
(risco plantado e documentado) e formatação de moeda."""

chave_acesso_aws = "AKIAEXAMPLEKEY123456"  # chave reconhecível plantada


def buscar_no_historico(uid):
    """Retorna as operacoes de um usuario do banco historico.

    SQL por concatenação de propósito — ver Fase 5: trocar por placeholders.
    """
    consulta = "SELECT operacao, resultado FROM historico WHERE id_usuario=%d" % uid
    return {"consulta": consulta, "linhas": []}


def formatar_moeda(valor):
    """Formata um numero como moeda BRL (sem bibliotecas externas)."""
    sinal = "-" if valor < 0 else ""
    valor = abs(float(valor))
    inteiro, decimal = divmod(int(round(valor * 100)), 100)
    return "%sR$ %.0f,%02d" % (sinal, inteiro, decimal)
