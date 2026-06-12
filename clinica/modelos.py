"""Estruturas de dados do domínio: Atendimento, Sessao e Consultorio.

Cada estrutura foi escolhida para espelhar diretamente o enunciado:
um consultório TEM duas sessões; uma sessão TEM uma lista ordenada de
atendimentos; um atendimento é um valor imutável (nome + duração).
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Atendimento:
    """Um pedido de atendimento. É imutável (frozen) porque, depois de lido do
    arquivo, nunca muda — só é movido de uma sessão para outra. Ser imutável
    também o torna *hasheável*, útil em conjuntos durante os testes."""

    nome: str
    duracao: int          # em minutos (expresso = 10)
    expresso: bool = False

    @property
    def rotulo_duracao(self) -> str:
        """Como a duração aparece na agenda impressa."""
        return "expresso" if self.expresso else f"{self.duracao}min"


@dataclass
class Sessao:
    """Uma "caixa" de tempo (manhã ou tarde) de um consultório.

    A lista `atendimentos` é ordenada de propósito: a ordem em que os
    atendimentos entram é exatamente a ordem em que serão impressos e em que
    os horários são calculados (08:00, 08:00+dur1, ...)."""

    rotulo: str           # "manhã" ou "tarde"
    inicio: int           # minutos desde a meia-noite em que a sessão começa
    teto: int             # limite superior de ocupação (em minutos)
    estrito: bool         # True  -> ocupação deve ser  < teto
                          # False -> ocupação deve ser <= teto
    minimo: int = 0       # ocupação mínima para a sessão ser válida (tarde=210)
    atendimentos: List[Atendimento] = field(default_factory=list)

    @property
    def ocupacao(self) -> int:
        """Total de minutos já agendados nesta sessão."""
        return sum(a.duracao for a in self.atendimentos)

    @property
    def folga(self) -> int:
        """Minutos ainda disponíveis até o teto (usado no 'melhor encaixe')."""
        return self.teto - self.ocupacao

    @property
    def fim(self) -> int:
        """Horário (minutos desde a meia-noite) em que o último atendimento
        termina — ou seja, quando começa a higienização/reunião."""
        return self.inicio + self.ocupacao

    def cabe(self, atendimento: Atendimento) -> bool:
        """Este atendimento ainda cabe sem estourar o teto da sessão?"""
        nova_ocupacao = self.ocupacao + atendimento.duracao
        if self.estrito:
            return nova_ocupacao < self.teto
        return nova_ocupacao <= self.teto

    @property
    def valida(self) -> bool:
        """A sessão respeita teto E mínimo? (a tarde tem mínimo; a manhã não)."""
        oc = self.ocupacao
        topo_ok = oc < self.teto if self.estrito else oc <= self.teto
        return topo_ok and oc >= self.minimo

    def adicionar(self, atendimento: Atendimento) -> None:
        self.atendimentos.append(atendimento)


@dataclass
class Consultorio:
    """Um consultório = uma manhã + uma tarde, com agenda independente."""

    numero: int
    manha: Sessao
    tarde: Sessao

    @property
    def sessoes(self) -> List[Sessao]:
        return [self.manha, self.tarde]

    @property
    def valido(self) -> bool:
        return self.manha.valida and self.tarde.valida
