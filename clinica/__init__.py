"""Pacote da clínica veterinária: parser, modelos, escalonador e relatório.

A organização das agendas é, no fundo, um problema de *empacotamento*
(bin packing): cada sessão é uma "caixa" com capacidade de tempo e cada
atendimento é um item com um "tamanho" em minutos. O objetivo é usar o
menor número possível de consultórios respeitando as regras da clínica.
"""

from .modelos import Atendimento, Sessao, Consultorio
from .escalonador import organizar
from .parser import carregar, parse_linha
from .relatorio import formatar_agenda, formatar_horario

__all__ = [
    "Atendimento",
    "Sessao",
    "Consultorio",
    "organizar",
    "carregar",
    "parse_linha",
    "formatar_agenda",
    "formatar_horario",
]
