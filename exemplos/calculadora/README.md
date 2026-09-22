# Calculadora de balcão

Programa de exemplo **feito para ser destrinchado** pelo Instalador: pequeno, com
propósito real (aritmética com histórico de sessão) e com falhas plantadas de
propósito — credencial em claro, `eval`, `except` genérico, `shell=True`,
`DEBUG` ligado e um `TODO` — para o Cético ter onde morder e o curso nascer
com debate de verdade.

## Uso

```bash
python3 calculadora.py + 2 3
python3 calculadora.py / 10 4 --historico
python3 calculadora.py expr "(2+3)*4"   # modo avançado (usa eval — veja a Fase 5)
```

## Gerar o curso dela

```bash
cd ..   # raiz do repositório Instalador
python3 instalador curso exemplos/calculadora
python3 instalador chat exemplos/calculadora --fase 5
```
