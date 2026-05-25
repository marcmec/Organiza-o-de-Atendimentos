"""
Agendador de Atendimentos Clínicos
===================================
Problema: distribuir n atendimentos em consultórios de capacidade fixa (SESSION_DURATION
minutos por sessão), minimizando o número de consultórios abertos.

Estratégia: variante de First-Fit Decreasing (FFD) com prioridade para expressos.
"""

from __future__ import annotations
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Duração de cada sessão em minutos (8 horas de trabalho)
SESSION_DURATION = 480


# ──────────────────────────────────────────────
# Estruturas de dados
# ──────────────────────────────────────────────

@dataclass
class Atendimento:
    """Representa um único atendimento (consulta)."""
    id: int
    paciente: str
    duracao: int          # em minutos
    tipo: str             # "normal" | "expresso"

    def __post_init__(self):
        if self.duracao <= 0:
            raise ValueError(f"Atendimento {self.id}: duração deve ser positiva.")
        if self.tipo not in ("normal", "expresso"):
            raise ValueError(f"Atendimento {self.id}: tipo inválido '{self.tipo}'.")
        if self.duracao > SESSION_DURATION:
            raise ValueError(
                f"Atendimento {self.id}: duração {self.duracao} excede a sessão "
                f"({SESSION_DURATION} min)."
            )


@dataclass
class Consultorio:
    """Um consultório com capacidade de SESSION_DURATION minutos por sessão."""
    numero: int
    capacidade: int = SESSION_DURATION
    tempo_disponivel: int = field(init=False)
    atendimentos: List[Atendimento] = field(default_factory=list)

    def __post_init__(self):
        self.tempo_disponivel = self.capacidade

    @property
    def tempo_usado(self) -> int:
        return self.capacidade - self.tempo_disponivel

    def pode_atender(self, atendimento: Atendimento) -> bool:
        return self.tempo_disponivel >= atendimento.duracao

    def alocar(self, atendimento: Atendimento) -> None:
        if not self.pode_atender(atendimento):
            raise RuntimeError(
                f"Consultório {self.numero} sem espaço para atendimento {atendimento.id}."
            )
        self.tempo_disponivel -= atendimento.duracao
        self.atendimentos.append(atendimento)

    def __repr__(self) -> str:
        return (f"Consultório {self.numero} "
                f"[{self.tempo_usado}/{self.capacidade} min | "
                f"{len(self.atendimentos)} atendimentos]")


# ──────────────────────────────────────────────
# Leitura de entrada
# ──────────────────────────────────────────────

def ler_atendimentos(caminho: str) -> List[Atendimento]:
    """
    Formato esperado de atendimentos.txt:
        <n>
        <id>,<paciente>,<duracao_min>,<tipo>
        ...
    Exemplo:
        5
        1,Ana Silva,30,normal
        2,Bob Souza,10,expresso
    """
    atendimentos: List[Atendimento] = []
    with open(caminho, encoding="utf-8") as f:
        n = int(f.readline().strip())
        for linha_num, linha in enumerate(f, start=2):
            linha = linha.strip()
            if not linha:
                continue
            partes = [p.strip() for p in linha.split(",")]
            if len(partes) != 4:
                raise ValueError(f"Linha {linha_num}: formato inválido → '{linha}'")
            id_, paciente, duracao, tipo = partes
            atendimentos.append(
                Atendimento(int(id_), paciente, int(duracao), tipo)
            )
    if len(atendimentos) != n:
        raise ValueError(
            f"Cabeçalho diz {n} atendimentos, mas foram lidos {len(atendimentos)}."
        )
    return atendimentos


# ──────────────────────────────────────────────
# Algoritmo principal: FFD com prioridade para expressos
# ──────────────────────────────────────────────

def _first_fit(atendimentos: List[Atendimento],
               consultorios: List[Consultorio]) -> List[Consultorio]:
    """
    Para cada atendimento, tenta encaixar no primeiro consultório com espaço.
    Se nenhum couber, abre um novo.
    """
    for atend in atendimentos:
        alocado = False
        for c in consultorios:
            if c.pode_atender(atend):
                c.alocar(atend)
                alocado = True
                break
        if not alocado:
            novo = Consultorio(numero=len(consultorios) + 1)
            novo.alocar(atend)
            consultorios.append(novo)
    return consultorios


def escalonar(atendimentos: List[Atendimento],
              capacidade: int = SESSION_DURATION) -> List[Consultorio]:
    """
    Algoritmo FFD modificado:

    1. Separa expressos e normais.
    2. Ordena normais por duração decrescente (heurística FFD).
    3. Aloca expressos primeiro — eles têm prioridade de chegada e
       costumam ser curtos, sobrando espaço para agregar normais depois.
    4. Aplica First-Fit nos normais (já ordenados).

    Retorna a lista de consultórios abertos.
    """
    expressos = [a for a in atendimentos if a.tipo == "expresso"]
    normais   = sorted(
        [a for a in atendimentos if a.tipo == "normal"],
        key=lambda a: a.duracao,
        reverse=True          # maiores primeiro → menos desperdício
    )

    consultorios: List[Consultorio] = []

    # Fase 1: expressos (sem reordenação — respeitamos a ordem de chegada)
    _first_fit(expressos, consultorios)

    # Fase 2: normais em ordem decrescente de duração
    _first_fit(normais, consultorios)

    return consultorios


# ──────────────────────────────────────────────
# Saída / relatório
# ──────────────────────────────────────────────

def imprimir_resultado(consultorios: List[Consultorio]) -> None:
    linha = "─" * 55
    print(f"\n{linha}")
    print(f"  TOTAL DE CONSULTÓRIOS ABERTOS: {len(consultorios)}")
    print(f"{linha}\n")
    for c in consultorios:
        print(f"  {c}")
        for a in c.atendimentos:
            tag = " ⚡EXPRESSO" if a.tipo == "expresso" else ""
            print(f"    #{a.id:>3} | {a.paciente:<20} | {a.duracao:>3} min{tag}")
        print()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    caminho = argv[0] if argv else "atendimentos.txt"

    try:
        atendimentos = ler_atendimentos(caminho)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO ao ler entrada: {e}", file=sys.stderr)
        return 1

    if not atendimentos:
        print("Nenhum atendimento encontrado.")
        return 0

    consultorios = escalonar(atendimentos)
    imprimir_resultado(consultorios)
    return 0


if __name__ == "__main__":
    sys.exit(main())
