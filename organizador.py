# -*- coding: utf-8 -*-
"""
Sistema de Organização de Atendimentos

Este programa lê uma lista de atendimentos de um arquivo .txt e distribui
automaticamente os atendimentos entre consultórios, respeitando horários de
funcionamento, intervalo para higienização e reunião de encerramento.

Formato aceito no arquivo de entrada:
    Nome do atendimento 60min
    Nome do atendimento expresso

Atendimento expresso equivale a 10 minutos.
"""

import re
import sys
from dataclasses import dataclass, field
from typing import List

# Horários convertidos para minutos
MANHA_INICIO = 8 * 60                 # 08:00
MANHA_FIM = 11 * 60 + 30              # 11:30
TARDE_INICIO = 13 * 60 + 30           # 13:30
REUNIAO_MINIMA = 17 * 60              # 17:00
REUNIAO_MAXIMA = 18 * 60              # antes de 18:00

CAPACIDADE_MANHA = MANHA_FIM - MANHA_INICIO
CAPACIDADE_TARDE = REUNIAO_MAXIMA - TARDE_INICIO - 1
DURACAO_EXPRESSO = 10


@dataclass
class Atendimento:
    nome: str
    duracao: int
    expresso: bool = False


@dataclass
class Periodo:
    inicio: int
    capacidade: int
    atendimentos: List[Atendimento] = field(default_factory=list)

    @property
    def tempo_usado(self) -> int:
        return sum(atendimento.duracao for atendimento in self.atendimentos)

    @property
    def tempo_livre(self) -> int:
        return self.capacidade - self.tempo_usado

    def pode_adicionar(self, atendimento: Atendimento) -> bool:
        return atendimento.duracao <= self.tempo_livre

    def adicionar(self, atendimento: Atendimento) -> bool:
        if self.pode_adicionar(atendimento):
            self.atendimentos.append(atendimento)
            return True
        return False


@dataclass
class Consultorio:
    numero: int
    manha: Periodo = field(default_factory=lambda: Periodo(MANHA_INICIO, CAPACIDADE_MANHA))
    tarde: Periodo = field(default_factory=lambda: Periodo(TARDE_INICIO, CAPACIDADE_TARDE))


def converter_hora(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def ler_atendimentos(texto: str) -> List[Atendimento]:
    atendimentos = []

    for numero_linha, linha in enumerate(texto.splitlines(), start=1):
        linha = linha.strip()

        if not linha or linha.startswith("#"):
            continue

        if re.search(r"\bexpresso\b$", linha, re.IGNORECASE):
            nome = re.sub(r"\s*expresso\s*$", "", linha, flags=re.IGNORECASE).strip()
            atendimentos.append(Atendimento(nome, DURACAO_EXPRESSO, True))
            continue

        resultado = re.search(r"(\d+)\s*min$", linha, re.IGNORECASE)
        if not resultado:
            raise ValueError(f"Linha {numero_linha} inválida: {linha}")

        nome = linha[:resultado.start()].strip()
        duracao = int(resultado.group(1))

        if duracao <= 0:
            raise ValueError(f"Linha {numero_linha}: duração deve ser maior que zero.")

        atendimentos.append(Atendimento(nome, duracao, False))

    return atendimentos


def menor_numero_consultorios(total_minutos: int) -> int:
    if total_minutos <= 0:
        return 1
    return max(1, -(-total_minutos // CAPACIDADE_TARDE))


def distribuir_em_periodos(atendimentos: List[Atendimento], periodos: List[Periodo]) -> List[Atendimento]:
    nao_alocados = []

    for atendimento in atendimentos:
        candidatos = [p for p in periodos if p.pode_adicionar(atendimento)]

        if candidatos:
            periodo_escolhido = min(candidatos, key=lambda p: p.tempo_usado)
            periodo_escolhido.adicionar(atendimento)
        else:
            nao_alocados.append(atendimento)

    return nao_alocados


def organizar(atendimentos: List[Atendimento]) -> List[Consultorio]:
    if not atendimentos:
        return []

    maior = max(a.duracao for a in atendimentos)
    if maior > CAPACIDADE_MANHA and maior > CAPACIDADE_TARDE:
        raise ValueError(f"Existe atendimento de {maior}min que não cabe em nenhum período.")

    total = sum(a.duracao for a in atendimentos)
    quantidade = menor_numero_consultorios(total)
    consultorios = [Consultorio(i + 1) for i in range(quantidade)]

    ordenados = sorted(atendimentos, key=lambda a: a.duracao, reverse=True)

    # Primeiro tenta preencher as tardes, pois elas precisam terminar próximas da reunião.
    sobras = distribuir_em_periodos(ordenados, [c.tarde for c in consultorios])

    # O que não couber à tarde vai para a manhã.
    sobras = distribuir_em_periodos(sobras, [c.manha for c in consultorios])

    # Se ainda houver sobras, cria novos consultórios até caber tudo.
    while sobras:
        novo = Consultorio(len(consultorios) + 1)
        consultorios.append(novo)
        sobras = distribuir_em_periodos(sobras, [novo.tarde, novo.manha])

    return consultorios


def validar(consultorios: List[Consultorio], atendimentos_originais: List[Atendimento]) -> List[str]:
    erros = []

    alocados = []
    for consultorio in consultorios:
        alocados.extend(consultorio.manha.atendimentos)
        alocados.extend(consultorio.tarde.atendimentos)

    if sorted(a.nome for a in alocados) != sorted(a.nome for a in atendimentos_originais):
        erros.append("Há atendimentos faltando ou duplicados.")

    for consultorio in consultorios:
        if consultorio.manha.tempo_usado > CAPACIDADE_MANHA:
            erros.append(f"Consultório {consultorio.numero}: manhã ultrapassou 11:30.")

        fim_tarde = TARDE_INICIO + consultorio.tarde.tempo_usado
        if consultorio.tarde.atendimentos and fim_tarde >= REUNIAO_MAXIMA:
            erros.append(f"Consultório {consultorio.numero}: reunião ficou às {converter_hora(fim_tarde)}, após o limite.")

    return erros


def formatar_periodo(periodo: Periodo) -> List[str]:
    linhas = []
    horario = periodo.inicio

    for atendimento in periodo.atendimentos:
        duracao = "expresso" if atendimento.expresso else f"{atendimento.duracao}min"
        linhas.append(f"  {converter_hora(horario)} - {atendimento.nome} ({duracao})")
        horario += atendimento.duracao

    return linhas


def gerar_agenda(consultorios: List[Consultorio]) -> str:
    linhas = []

    for consultorio in consultorios:
        linhas.append(f"Consultório {consultorio.numero}:")
        linhas.append(" Manhã:")
        linhas.extend(formatar_periodo(consultorio.manha))
        linhas.append(f"  {converter_hora(MANHA_FIM)} - Higienização")
        linhas.append(" Tarde:")
        linhas.extend(formatar_periodo(consultorio.tarde))
        fim_tarde = TARDE_INICIO + consultorio.tarde.tempo_usado
        linhas.append(f"  {converter_hora(fim_tarde)} - Reunião de encerramento")
        linhas.append("")

    return "\n".join(linhas)


def main() -> None:
    caminho = sys.argv[1] if len(sys.argv) > 1 else "atendimentos.txt"

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            texto = arquivo.read()

        atendimentos = ler_atendimentos(texto)
        consultorios = organizar(atendimentos)
        erros = validar(consultorios, atendimentos)

        if erros:
            for erro in erros:
                print(f"ERRO: {erro}", file=sys.stderr)
            sys.exit(1)

        print(gerar_agenda(consultorios))

    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}", file=sys.stderr)
        sys.exit(1)
    except ValueError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
