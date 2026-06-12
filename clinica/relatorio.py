"""Formatação da agenda final no layout pedido pelo enunciado."""

from typing import List

from .modelos import Consultorio
from .regras import HIGIENIZACAO


def formatar_horario(minutos_desde_meia_noite: int) -> str:
    """Converte 690 -> '11:30'."""
    horas, minutos = divmod(minutos_desde_meia_noite, 60)
    return f"{horas:02d}:{minutos:02d}"


def formatar_agenda(consultorios: List[Consultorio]) -> str:
    """Monta o texto final, um bloco por consultório.

    Cada atendimento é impresso com o horário em que COMEÇA, que é o início da
    sessão somado à duração de tudo que veio antes dele.
    """
    linhas: List[str] = []

    for consultorio in consultorios:
        linhas.append(f"Consultório {consultorio.numero}:")

        # --- Manhã ---
        relogio = consultorio.manha.inicio
        for atendimento in consultorio.manha.atendimentos:
            linhas.append(
                f"{formatar_horario(relogio)} {atendimento.nome} {atendimento.rotulo_duracao}"
            )
            relogio += atendimento.duracao
        # A higienização sempre começa às 11:30, ponto fixo da agenda.
        linhas.append(f"{formatar_horario(HIGIENIZACAO)} Higienização")

        # --- Tarde ---
        relogio = consultorio.tarde.inicio
        for atendimento in consultorio.tarde.atendimentos:
            linhas.append(
                f"{formatar_horario(relogio)} {atendimento.nome} {atendimento.rotulo_duracao}"
            )
            relogio += atendimento.duracao
        # A reunião começa quando o último atendimento da tarde termina.
        linhas.append(
            f"{formatar_horario(consultorio.tarde.fim)} Reunião de encerramento"
        )

        linhas.append("")  # linha em branco separando os consultórios

    return "\n".join(linhas).rstrip() + "\n"
