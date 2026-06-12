"""O coração da solução: distribuir os atendimentos pelos consultórios.

Estratégia (heurística gulosa em duas fases):

  Fase 0 - Estimar o número MÍNIMO de consultórios pela capacidade total.
  Fase 1 - Encher PRIMEIRO as tardes até atingirem o mínimo de 210 min
           (senão a reunião de encerramento começaria antes das 17:00).
  Fase 2 - Distribuir o restante por "melhor encaixe" (best-fit) entre as
           manhãs e a folga das tardes.

Se em algum ponto não couber tudo, abrimos um consultório a mais e tentamos de
novo. O detalhamento e a justificativa estão no RACIOCINIO.md.
"""

from typing import List, Optional

from .modelos import Atendimento, Sessao, Consultorio
from .regras import (
    INICIO_MANHA,
    INICIO_TARDE,
    CAP_MANHA,
    CAP_TARDE,
    MIN_TARDE,
    CAP_CONSULTORIO,
)


def _novo_consultorio(numero: int) -> Consultorio:
    """Cria um consultório vazio com as regras de manhã e tarde já aplicadas."""
    manha = Sessao(
        rotulo="manhã",
        inicio=INICIO_MANHA,
        teto=CAP_MANHA,      # 08:00 -> 11:30
        estrito=False,       # terminar ATÉ 11:30 (ocupação <= 210)
        minimo=0,            # a manhã não precisa ser preenchida
    )
    tarde = Sessao(
        rotulo="tarde",
        inicio=INICIO_TARDE,
        teto=CAP_TARDE,      # reunião antes das 18:00 -> ocupação < 270
        estrito=True,
        minimo=MIN_TARDE,    # reunião a partir das 17:00 -> ocupação >= 210
    )
    return Consultorio(numero=numero, manha=manha, tarde=tarde)


def numero_minimo_consultorios(total_minutos: int) -> int:
    """Limite inferior teórico: nem que todos os consultórios ficassem cheios,
    seriam necessários pelo menos ceil(total / capacidade_de_um) consultórios."""
    if total_minutos <= 0:
        return 0
    # divisão inteira "para cima" sem usar math.ceil (evita ponto flutuante)
    return -(-total_minutos // CAP_CONSULTORIO)


def _tentar_empacotar(atendimentos: List[Atendimento], k: int) -> Optional[List[Consultorio]]:
    """Tenta montar uma agenda válida usando exatamente `k` consultórios.

    Devolve a lista de consultórios se conseguir, ou None se algo não couber.
    """
    consultorios = [_novo_consultorio(i + 1) for i in range(k)]
    manhas = [c.manha for c in consultorios]
    tardes = [c.tarde for c in consultorios]

    # Atendimentos do maior para o menor: itens grandes são os mais difíceis de
    # encaixar, então tratamos eles primeiro (ideia clássica do "decreasing fit").
    pendentes = sorted(atendimentos, key=lambda a: a.duracao, reverse=True)

    # ----- FASE 1: garantir o mínimo de cada tarde -------------------------
    # Enquanto existir uma tarde abaixo de 210 min, escolhemos a MENOS cheia
    # (a mais necessitada) e colocamos nela o MAIOR atendimento que ainda cabe
    # sem ultrapassar o teto (< 270). Isso evita o erro clássico de deixar uma
    # tarde vazia — o que tornaria a reunião daquele consultório impossível.
    while True:
        abaixo_do_minimo = sorted(
            (t for t in tardes if t.ocupacao < t.minimo),
            key=lambda t: t.ocupacao,
        )
        if not abaixo_do_minimo:
            break

        progrediu = False
        for tarde in abaixo_do_minimo:
            escolhido = next((a for a in pendentes if tarde.cabe(a)), None)
            if escolhido is not None:
                tarde.adicionar(escolhido)
                pendentes.remove(escolhido)
                progrediu = True
                break

        if not progrediu:
            # Nenhuma tarde abaixo do mínimo conseguiu receber nenhum
            # atendimento restante -> esta configuração não fecha.
            return None

    # ----- FASE 2: distribuir o restante por melhor encaixe ----------------
    # Para cada atendimento restante (ainda em ordem decrescente), escolhemos a
    # sessão (manhã OU folga de uma tarde) onde ele cabe deixando a MENOR folga.
    # "Best-fit" desperdiça menos espaço e mantém as outras sessões abertas
    # para itens que ainda virão.
    for atendimento in pendentes:
        candidatas = [s for s in (tardes + manhas) if s.cabe(atendimento)]
        if not candidatas:
            return None  # estourou a capacidade: precisamos de mais 1 consultório
        melhor = min(candidatas, key=lambda s: s.folga)
        melhor.adicionar(atendimento)

    # ----- Validação final (defensiva) -------------------------------------
    if all(c.valido for c in consultorios):
        return consultorios
    return None


def organizar(atendimentos: List[Atendimento]) -> List[Consultorio]:
    """Organiza todos os atendimentos no MENOR número de consultórios válidos.

    Começamos pelo limite inferior teórico e, se a montagem falhar, abrimos um
    consultório de cada vez até conseguir (ou até esgotar as possibilidades).
    """
    if not atendimentos:
        return []

    total = sum(a.duracao for a in atendimentos)
    k_inicial = max(1, numero_minimo_consultorios(total))
    # Limite superior de segurança: nunca faz sentido ter mais consultórios do
    # que atendimentos.
    k_maximo = len(atendimentos)

    for k in range(k_inicial, k_maximo + 1):
        resultado = _tentar_empacotar(atendimentos, k)
        if resultado is not None:
            return resultado

    raise ValueError(
        "Não foi possível montar uma agenda válida: verifique se há atendimentos "
        "suficientes para preencher ao menos uma tarde (>= 210 min) e se nenhum "
        "atendimento isolado excede a capacidade de uma sessão."
    )
