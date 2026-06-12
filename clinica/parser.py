"""Leitura do arquivo de entrada (atendimentos.txt).

Cada linha tem a forma:  <nome do atendimento> <duração>
onde a duração é o ÚLTIMO token e vale uma de duas formas:
  - "<n>min"   -> n minutos        (ex.: "90min")
  - "expresso" -> 10 minutos       (atendimento rápido, ex.: vacina)

Decisão importante: olhamos apenas o ÚLTIMO token para descobrir a duração.
Assim o parser continua correto mesmo quando o NOME contém números — caso real
da entrada: "Aplicação de vacina V10 expresso" (o "V10" faz parte do nome).
"""

import re
from typing import List, Optional

from .modelos import Atendimento
from .regras import EXPRESSO_MIN

_PADRAO_MINUTOS = re.compile(r"^(\d+)min$", re.IGNORECASE)


def parse_linha(linha: str) -> Optional[Atendimento]:
    """Converte uma linha de texto em um Atendimento.

    Retorna None para linhas em branco. Levanta ValueError se a linha não
    terminar com uma duração reconhecível — falhar alto é melhor do que
    agendar silenciosamente um atendimento com duração errada.
    """
    linha = linha.strip()
    if not linha:
        return None

    partes = linha.split()
    marcador = partes[-1]
    nome = " ".join(partes[:-1]).strip()

    if not nome:
        raise ValueError(f"Linha sem nome de atendimento: {linha!r}")

    if marcador.lower() == "expresso":
        return Atendimento(nome=nome, duracao=EXPRESSO_MIN, expresso=True)

    correspondencia = _PADRAO_MINUTOS.match(marcador)
    if correspondencia:
        minutos = int(correspondencia.group(1))
        if minutos <= 0:
            raise ValueError(f"Duração inválida (<= 0) em: {linha!r}")
        return Atendimento(nome=nome, duracao=minutos, expresso=False)

    raise ValueError(f"Não reconheci a duração na linha: {linha!r}")


def parse_texto(texto: str) -> List[Atendimento]:
    """Converte um bloco de texto inteiro em lista de Atendimentos."""
    atendimentos = (parse_linha(linha) for linha in texto.splitlines())
    return [a for a in atendimentos if a is not None]


def carregar(caminho: str) -> List[Atendimento]:
    """Lê o arquivo de entrada e devolve a lista de Atendimentos."""
    with open(caminho, encoding="utf-8") as arquivo:
        return parse_texto(arquivo.read())
