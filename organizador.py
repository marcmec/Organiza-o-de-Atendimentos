# -*- coding: utf-8 -*-
"""
Organizador de Atendimentos - Clinica Veterinaria Comunitaria

Abordagem: duas fases com estrategia LPT (Longest Processing Time).

FASE 1 - Tardes: distribui atendimentos usando LPT balanceado entre N consultorios,
         onde N e calculado para que cada tarde fique entre 210 e 269 minutos.
FASE 2 - Manhas: o que nao coube nas tardes vai para as manhas (max 210 min cada),
         tambem com LPT.
"""

import re
import sys
from dataclasses import dataclass, field
from typing import List


# Constantes de tempo (em minutos desde 00:00)
MANHA_INICIO     = 8 * 60           # 08:00 -> 480 min
MANHA_FIM        = 11 * 60 + 30    # 11:30 -> 690 min
TARDE_INICIO     = 13 * 60 + 30    # 13:30 -> 810 min
REUNIAO_MINIMO   = 17 * 60         # 17:00 -> 1020 min
REUNIAO_MAXIMO   = 18 * 60         # 18:00 -> 1080 min

CAPACIDADE_MANHA = MANHA_FIM - MANHA_INICIO                # 210 min
TARDE_MIN        = REUNIAO_MINIMO - TARDE_INICIO            # 210 min (reuniao >= 17h)
TARDE_MAX        = REUNIAO_MAXIMO - TARDE_INICIO - 1        # 269 min (reuniao < 18h)
DURACAO_EXPRESSO = 10


# --- Estruturas de dados ---

@dataclass
class Atendimento:
    nome: str
    duracao: int
    expresso: bool = False


@dataclass
class Sessao:
    inicio: int
    capacidade: int
    atendimentos: List[Atendimento] = field(default_factory=list)

    @property
    def tempo_usado(self) -> int:
        return sum(a.duracao for a in self.atendimentos)

    @property
    def tempo_livre(self) -> int:
        return self.capacidade - self.tempo_usado

    def cabe(self, atendimento: Atendimento) -> bool:
        return self.tempo_livre >= atendimento.duracao

    def adicionar(self, atendimento: Atendimento) -> bool:
        if self.cabe(atendimento):
            self.atendimentos.append(atendimento)
            return True
        return False


@dataclass
class Consultorio:
    numero: int
    manha: Sessao = field(default_factory=lambda: Sessao(MANHA_INICIO, CAPACIDADE_MANHA))
    tarde: Sessao = field(default_factory=lambda: Sessao(TARDE_INICIO, TARDE_MAX))

    def sessoes(self) -> List[Sessao]:
        return [self.manha, self.tarde]


# --- Parser de entrada ---

def parse_atendimentos(texto: str) -> List[Atendimento]:
    """
    Formato aceito por linha:
        <nome> <N>min    - duracao explicita em minutos
        <nome> expresso  - atendimento rapido de 10 min
    Linhas em branco e comentarios (#) sao ignorados.
    """
    resultado = []
    for linha in texto.strip().splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if re.search(r'\bexpresso\b', linha, re.IGNORECASE):
            nome = re.sub(r'\s*expresso\s*$', '', linha, flags=re.IGNORECASE).strip()
            resultado.append(Atendimento(nome=nome, duracao=DURACAO_EXPRESSO, expresso=True))
        else:
            m = re.search(r'(\d+)\s*min\s*$', linha, re.IGNORECASE)
            if not m:
                raise ValueError(f"Linha nao reconhecida: '{linha}'")
            resultado.append(Atendimento(
                nome=linha[: m.start()].strip(),
                duracao=int(m.group(1)),
                expresso=False,
            ))
    return resultado


# --- Calculo do numero minimo de consultorios ---

def _min_consultorios(total_minutos: int) -> int:
    """
    Calcula quantos consultorios sao necessarios.

    Cada tarde deve ter entre TARDE_MIN (210) e TARDE_MAX (269) minutos.
    Para que todos os atendimentos caibam nas tardes:
      - N * TARDE_MAX >= total_minutos  => N >= ceil(total / TARDE_MAX)
      - N * TARDE_MIN <= total_minutos  => N <= floor(total / TARDE_MIN)
    Tomamos o menor N que satisfaz a primeira condicao.
    Se total_minutos > N * TARDE_MAX para qualquer N viavel, o excedente vai para a manha.
    """
    if total_minutos <= 0:
        return 1
    # Minimo de consultorios para caber em TARDE_MAX cada
    n = -(-total_minutos // TARDE_MAX)  # equivale a ceil(total / TARDE_MAX)
    return max(1, n)


# --- Algoritmo LPT para alocacao ---

def _lpt_tarde(itens: List[Atendimento], tardes: List[Sessao]) -> List[Atendimento]:
    """
    Longest Processing Time para sessoes da tarde.
    Para cada item (maior primeiro), aloca na tarde com menor carga atual
    que ainda consegue receber o item sem ultrapassar TARDE_MAX.
    Retorna itens que nao couberam em nenhuma tarde.
    """
    sobras = []
    for item in itens:
        # Tardes candidatas: tem espaco para o item
        candidatas = [(s.tempo_usado, i) for i, s in enumerate(tardes) if s.cabe(item)]
        if candidatas:
            # Escolhe a tarde com menor carga (balanceamento LPT)
            _, idx = min(candidatas)
            tardes[idx].adicionar(item)
        else:
            sobras.append(item)
    return sobras


def _lpt_manha(itens: List[Atendimento], manhas: List[Sessao]) -> List[Atendimento]:
    """
    LPT para sessoes da manha.
    Para cada item, aloca na manha com menor carga que ainda aceita o item.
    Retorna itens que nao couberam.
    """
    sobras = []
    for item in itens:
        candidatas = [(s.tempo_usado, i) for i, s in enumerate(manhas) if s.cabe(item)]
        if candidatas:
            _, idx = min(candidatas)
            manhas[idx].adicionar(item)
        else:
            sobras.append(item)
    return sobras


# --- Algoritmo principal ---

def organizar(atendimentos: List[Atendimento]) -> List[Consultorio]:
    """
    FASE 1 - Tardes (LPT balanceado):
        Calcula N = numero minimo de consultorios para que o total caiba em tardes de 210-269 min.
        Ordena atendimentos do maior ao menor e aloca na tarde menos carregada (LPT).
        Se um item nao couber em nenhuma tarde existente, abre novo consultorio.

    FASE 2 - Manhas (LPT):
        Itens que nao foram para nenhuma tarde vao para as manhas (max 210 min).
        LPT: aloca no manha menos carregada que ainda aceita o item.
        Abre novos consultorios se necessario.

    Por que LPT ao inves de FFD classico?
        FFD (First-Fit Decreasing) aloca no primeiro bin que aceita o item, o que leva
        a bins cheios enquanto outros ficam vazios. Com a restricao de MINIMO (tarde >= 210),
        bins vazios sao proibidos. LPT distribui a carga mais uniformemente ao escolher
        sempre o bin com menor carga atual, reduzindo drasticamente o risco de tarde deficitaria.
    """
    if not atendimentos:
        return []

    # Verifica se ha atendimento maior que qualquer sessao
    maior = max(a.duracao for a in atendimentos)
    if maior > TARDE_MAX and maior > CAPACIDADE_MANHA:
        raise ValueError(
            f"Atendimento de {maior}min excede a capacidade maxima de qualquer sessao."
        )

    total = sum(a.duracao for a in atendimentos)
    n = _min_consultorios(total)

    consultorios: List[Consultorio] = [Consultorio(numero=i + 1) for i in range(n)]
    tardes = [c.tarde for c in consultorios]
    manhas = [c.manha for c in consultorios]

    # Ordena do maior para o menor (LPT)
    ordenados = sorted(atendimentos, key=lambda a: -a.duracao)

    # --- FASE 1: tardes ---
    sobra_tarde = _lpt_tarde(ordenados, tardes)

    # Se ainda ha sobras (itens muito grandes para qualquer tarde), abre mais consultorios
    while sobra_tarde:
        novo = Consultorio(numero=len(consultorios) + 1)
        consultorios.append(novo)
        tardes.append(novo.tarde)
        manhas.append(novo.manha)
        sobra_tarde = _lpt_tarde(sobra_tarde, [novo.tarde])
        if sobra_tarde and not novo.tarde.atendimentos:
            # Item nao cabe na tarde: vai para manha
            break

    # --- FASE 2: manhas ---
    # Itens que nao couberam em nenhuma tarde
    para_manha = sorted(sobra_tarde, key=lambda a: -a.duracao)
    sobra_manha = _lpt_manha(para_manha, manhas)

    while sobra_manha:
        novo = Consultorio(numero=len(consultorios) + 1)
        consultorios.append(novo)
        manhas.append(novo.manha)
        tardes.append(novo.tarde)
        sobra_manha = _lpt_manha(sobra_manha, [novo.manha])

    # Renumera
    for i, c in enumerate(consultorios):
        c.numero = i + 1

    return consultorios


# --- Formatacao de saida ---

def minutos_para_hhmm(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def formatar_saida(consultorios: List[Consultorio]) -> str:
    linhas = []
    for c in consultorios:
        linhas.append(f"Consultorio {c.numero}:")
        cursor = c.manha.inicio
        for a in c.manha.atendimentos:
            sufixo = "expresso" if a.expresso else f"{a.duracao}min"
            linhas.append(f"  {minutos_para_hhmm(cursor)} {a.nome} {sufixo}")
            cursor += a.duracao
        linhas.append(f"  {minutos_para_hhmm(MANHA_FIM)} Higienizacao")
        cursor = c.tarde.inicio
        for a in c.tarde.atendimentos:
            sufixo = "expresso" if a.expresso else f"{a.duracao}min"
            linhas.append(f"  {minutos_para_hhmm(cursor)} {a.nome} {sufixo}")
            cursor += a.duracao
        linhas.append(f"  {minutos_para_hhmm(cursor)} Reuniao de encerramento")
        linhas.append("")
    return "\n".join(linhas)


# --- Validacao ---

def validar(consultorios: List[Consultorio], originais: List[Atendimento]) -> List[str]:
    erros = []
    alocados = [a for c in consultorios for s in c.sessoes() for a in s.atendimentos]

    if sorted(a.nome for a in alocados) != sorted(a.nome for a in originais):
        erros.append("Nem todos os atendimentos foram alocados ou houve duplicatas.")

    for c in consultorios:
        if c.manha.tempo_usado > CAPACIDADE_MANHA:
            erros.append(f"Consultorio {c.numero}: manha excede 11:30.")
        fim = TARDE_INICIO + c.tarde.tempo_usado
        if fim < REUNIAO_MINIMO:
            erros.append(
                f"Consultorio {c.numero}: reuniao as {minutos_para_hhmm(fim)} - antes das 17:00."
            )
        if fim >= REUNIAO_MAXIMO:
            erros.append(
                f"Consultorio {c.numero}: reuniao as {minutos_para_hhmm(fim)} - 18:00 ou depois."
            )

    return erros


# --- Entrypoint ---

def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "atendimentos.txt"
    try:
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"Arquivo '{caminho}' nao encontrado.", file=sys.stderr)
        sys.exit(1)

    atendimentos = parse_atendimentos(texto)
    consultorios = organizar(atendimentos)
    erros = validar(consultorios, atendimentos)

    if erros:
        for e in erros:
            print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(2)

    print(formatar_saida(consultorios))


if __name__ == "__main__":
    main()
