# -*- coding: utf-8 -*-
"""Testes mínimos da calculadora — rede de proteção que o Convicto cita."""
import unittest
from calculadora import Calculadora, converter
from util import formatar_moeda


class TestesCalculadora(unittest.TestCase):
    def setUp(self):
        self.c = Calculadora()

    def test_somar(self):
        self.assertEqual(self.c.somar(2, 3), 5)

    def test_dividir_por_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.c.dividir(1, 0)

    def test_expressao_whitelist(self):
        self.assertEqual(self.c.expressao("2+2*2"), 6)

    def test_converter(self):
        self.assertEqual(converter("10"), 10)
        self.assertIsNone(converter("abc"))

    def test_moeda(self):
        self.assertEqual(formatar_moeda(1234.5), "R$ 1234,50")


if __name__ == "__main__":
    unittest.main()
