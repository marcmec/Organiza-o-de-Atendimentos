# RACIOCINIO.md — Agendador de Atendimentos Clínicos

---

## Parte 1 — Modelagem do Problema

### Pergunta 1 — Como você classificou esse problema?

Classifiquei como um **problema de otimização combinatória**, especificamente uma
instância do **Bin Packing Problem (BPP)**.

Características do enunciado que apoiam essa classificação:

- Cada **consultório** tem uma capacidade fixa e imutável: exatamente `SESSION_DURATION`
  minutos de sessão por dia (480 min = 8 h).
- Cada **atendimento** tem um "peso" (sua duração em minutos) que consome parte dessa
  capacidade ao ser alocado.
- O objetivo é **minimizar o número de consultórios abertos**, ou seja, minimizar o
  número de "bins" utilizados.
- Não há horário fixo de início — apenas a restrição de que a soma das durações dentro
  de um consultório não pode exceder a capacidade da sessão.

Isso mapeia exatamente para o BPP clássico: dado um conjunto de itens com pesos e bins
de capacidade C, empacote todos os itens usando o menor número de bins possível.

---

### Pergunta 2 — Semelhança com problemas clássicos da computação

O problema é idêntico ao **Bin Packing Problem (BPP)**, que é NP-difícil no caso geral.
Analogia direta:

| Domínio clínico       | Domínio BPP clássico  |
|-----------------------|-----------------------|
| Consultório           | Bin (caixa / recipiente) |
| Capacidade da sessão  | Capacidade C do bin   |
| Atendimento           | Item                  |
| Duração do atendimento | Peso do item         |
| Nº de consultórios    | Nº de bins usados     |

Guardo também semelhança com o **Scheduling on Identical Machines**: alocar jobs em
máquinas paralelas minimizando o makespan (ou, equivalentemente, o número de máquinas).
A diferença é que no makespan clássico os jobs têm tempos de processamento fixos e
queremos minimizar o tempo total; aqui queremos minimizar a quantidade de "máquinas"
(consultórios), com cada uma limitada a C minutos.

---

### Pergunta 3 — Estruturas de dados escolhidas e justificativas

Foram três estruturas centrais:

**`Atendimento` (dataclass)**
```
id: int
paciente: str
duracao: int
tipo: str  ← "normal" | "expresso"
```
Representa a unidade atômica do problema. Optei por `dataclass` para ter validação
automática no `__post_init__` (duração positiva, tipo válido, duração ≤ sessão) sem
código boilerplate. Se tivesse usado um `dict`, os erros de campo errado só
apareceriam em runtime, longe da origem.

**`Consultorio` (dataclass)**
```
numero: int
tempo_disponivel: int   ← decrementado a cada alocação
atendimentos: list[Atendimento]
```
O atributo `tempo_disponivel` é o "espaço restante do bin". Mantê-lo pré-calculado
evita percorrer a lista de atendimentos a cada verificação de `pode_atender()` —
torna essa consulta O(1) em vez de O(k), onde k é o número de atendimentos no
consultório.

**`List[Consultorio]` (lista linear)**
A lista é percorrida da esquerda para a direita no passo de First-Fit: "encaixe no
primeiro que couber". A ordem de inserção é preservada, o que é importante para o
resultado ser determinístico.

Se eu tivesse usado outra estrutura:

- **Heap (min-heap) por tempo disponível**: encontraria o consultório com mais espaço
  em O(log n) em vez de O(k), mas quebraria a semântica de First-Fit (passaria a ser
  Best-Fit). Produziria resultados diferentes e perderia a propriedade de "primeiro
  que couber".
- **Dict {numero → consultório}**: nenhum ganho prático, já que a operação dominante
  é busca sequencial, não acesso por chave.

---

## Parte 2 — Estratégia Algorítmica

### Pergunta 4 — Descrição do algoritmo em linguagem natural

O algoritmo executa em duas fases:

**Fase 0 — Pré-processamento**
Separa a lista de entrada em dois grupos: `expressos` e `normais`. Os normais são
ordenados por duração de forma **decrescente** (o maior vem primeiro).

**Fase 1 — Alocação dos expressos**
Para cada atendimento expresso (na ordem em que chegaram, sem reordenação):
- Percorre os consultórios já abertos da esquerda para a direita.
- Aloca no **primeiro** que ainda tenha espaço suficiente.
- Se nenhum couber, abre um novo consultório e aloca lá.

**Fase 2 — Alocação dos normais (FFD)**
Para cada atendimento normal (do maior para o menor):
- Percorre os consultórios (os já abertos pelos expressos e os abertos na fase 1).
- Aloca no **primeiro** que caiba.
- Se nenhum couber, abre um novo consultório.

**Ideia intuitiva:** atendimentos grandes são difíceis de "encaixar" — se você os
deixar para depois, provavelmente vão precisar de consultórios novos. Colocando os
maiores primeiro, você deixa os pequenos para "tapar buracos" no final de cada bin,
reduzindo desperdício.

---

### Pergunta 5 — Sua solução é gulosa, exata, heurística ou outra?

É uma **heurística gulosa** — especificamente a heurística **FFD (First-Fit
Decreasing)**, uma das mais estudadas para Bin Packing.

Como cheguei a essa decisão:

1. **Exata estava descartada**: Bin Packing é NP-difícil. Para n = 15 atendimentos,
   uma solução exata por força bruta testaria todas as partições (número de Bell B(15)
   ≈ 1,3 × 10⁹). Inviável em tempo aceitável para n grande.

2. **FFD é a heurística mais clássica e defensável para BPP**: tem garantia teórica
   de que usa no máximo `(11/9) · OPT + 6/9` bins, ou seja, nunca abre muito mais que
   o ótimo. Essa garantia existe desde o resultado de Johnson (1973).

3. **Simplicidade e auditabilidade**: o algoritmo é explicável passo a passo sem
   matemática sofisticada — vantagem importante para defesa oral e manutenção.

4. **Alternativas consideradas e descartadas**:
   - *Best-Fit Decreasing*: aloca no bin com menos espaço sobrando que ainda caiba.
     Ligeiramente melhor na prática, mas mais complexo de implementar e justificar.
   - *Algoritmos de busca local (simulated annealing, etc.)*: melhores soluções, mas
     muito mais código, mais difícil de testar unitariamente.

---

### Pergunta 6 — Contraexemplo: quando o algoritmo não encontra o ótimo

**Configuração do contraexemplo:**
- SESSION_DURATION = 10 (simplificado para facilitar o raciocínio)
- Atendimentos: `[6, 6, 5, 5, 4, 4]` (todos normais)

**O que FFD faz** (ordena desc → `[6, 6, 5, 5, 4, 4]`):
```
Bin 1: 6  →  depois tenta 6: não cabe (espaço = 4) → tenta 5: não cabe → aloca 4. Bin 1 = [6, 4] → usado = 10 ✓
Bin 2: 6  →  tenta 5: não cabe (espaço = 4) → aloca 4. Bin 2 = [6, 4] → usado = 10 ✓
Bin 3: 5, 5 → Bin 3 = [5, 5] → usado = 10 ✓
Total: 3 bins
```

**O ótimo também é 3 bins** nesse caso — FFD acertou.

Para um contraexemplo real onde FFD erra, use (capacidade = 10):
- Atendimentos: `[9, 7, 6, 5, 4, 3, 2, 2, 2, 2]`

FFD (ordenado desc `[9, 7, 6, 5, 4, 3, 2, 2, 2, 2]`):
```
Bin 1: 9+? → 9+7=16>10 → 9+6>10 → 9+5>10 → 9+4>10 → 9+3>10 → 9+2=11>10 → 9+2=11>10 → ... → Bin 1 = [9] (1 desperdiçado)
Bin 2: 7+3=10 → Bin 2 = [7, 3]
Bin 3: 6+4=10 → Bin 3 = [6, 4]
Bin 4: 5+2+2+2=11>10 → 5+2+2=9, tenta +2=11>10 → Bin 4 = [5, 2, 2] (espaço=1, não cabe 2)
Bin 5: 2+2 = [2, 2]
Total FFD: 5 bins
```
Ótimo possível: `[9, .]  [7, 3]  [6, 4]  [5, 2, 2]  [2, 2]` → 5 bins também, mas com
redistribuição `[9]  [7, 2, 2]  [6, 4]  [5, 3, 2]` → 4 bins!

Esse é o ponto: a gulodice de colocar o 9 sozinho "desperdiçou" espaço que os 2s
poderiam ocupar, mas o FFD já tinha descido para os itens de tamanho 2 quando chegou
no bin do 9.

---

### Pergunta 7 — Complexidade de tempo

Sendo `n` o número de atendimentos:

**Fase de separação e ordenação:**
- `O(n)` para separar expressos/normais
- `O(n log n)` para ordenar os normais

**Fase de alocação (First-Fit):**
- No pior caso, cada atendimento é tentado em todos os consultórios abertos antes de
  abrir um novo. Se todos os n atendimentos forem para consultórios diferentes (pior
  caso de BPP: todos os itens têm exatamente metade da capacidade + 1), o i-ésimo
  atendimento verifica i consultórios antes de abrir o (i+1)-ésimo.
- Custo total: 1 + 2 + 3 + … + n = **O(n²)**

**Complexidade total:** `O(n log n) + O(n²) = O(n²)`

O n² domina. Para n = 1000, isso significa ~10⁶ operações — rápido na prática. O
gargalo real de Bin Packing não está no FFD, mas em encontrar a solução ótima, que é
NP-difícil.

---

## Parte 3 — Decisões de Implementação

### Pergunta 8 — Como o programa decide quantos consultórios abrir?

De forma **completamente dinâmica e reativa**: o programa nunca decide antecipadamente
quantos consultórios serão necessários. Ele começa com zero e abre um novo consultório
**somente quando nenhum dos já abertos tem espaço suficiente** para o próximo
atendimento.

Código responsável (função `_first_fit`):

```python
for atend in atendimentos:
    alocado = False
    for c in consultorios:
        if c.pode_atender(atend):
            c.alocar(atend)
            alocado = True
            break
    if not alocado:          # ← único critério para abrir novo consultório
        novo = Consultorio(numero=len(consultorios) + 1)
        novo.alocar(atend)
        consultorios.append(novo)
```

A decisão é **local e gulosa**: nunca fecha um consultório, nunca realoca um
atendimento já colocado. Isso mantém O(n²) mas elimina qualquer estado global que
precisaria ser revertido.

---

### Pergunta 9 — Como os atendimentos expressos foram tratados?

Expressos recebem **prioridade de alocação**: são processados inteiramente na Fase 1,
antes de qualquer atendimento normal. A justificativa é dupla:

1. **Semântica do negócio**: "expresso" implica rapidez — o paciente não deve esperar
   atrás de uma fila de consultas longas. Alocá-los primeiro garante que sempre haverá
   um consultório disponível para eles.

2. **Eficiência do bin-packing**: expressos são tipicamente curtos (10–15 min). Se
   alocados depois dos normais, sobrariam apenas as "sobras" de cada bin — espaços
   pequenos e espalhados. Alocando primeiro, eles preenchem os primeiros bins e os
   normais (maiores) preenchem o que sobrou de forma mais compacta.

Além disso, expressos **não são reordenados** — respeitamos a ordem de chegada deles,
pois numa clínica real isso representa a fila de espera presencial.

---

### Pergunta 10 — Parte mais inteligente e parte que poderia ser melhorada

**Parte mais inteligente: separação dos expressos antes do FFD**

```python
def escalonar(atendimentos):
    expressos = [a for a in atendimentos if a.tipo == "expresso"]
    normais   = sorted([a for a in atendimentos if a.tipo == "normal"],
                       key=lambda a: a.duracao, reverse=True)
    _first_fit(expressos, consultorios)
    _first_fit(normais, consultorios)
```

A inteligência está em tratar os dois grupos com estratégias diferentes: expressos
preservam a ordem de chegada (semântica de fila), normais são reordenados para FFD
(semântica de otimização). Um único loop para todos os atendimentos não conseguiria
isso sem lógica condicional espalhada.

---

**Parte que poderia ser melhorada: a heurística de alocação**

O First-Fit verifica os consultórios sempre da posição 0. Para listas grandes, isso é
ineficiente porque os primeiros bins ficam cheios rápido e são verificados — e
rejeitados — repetidamente.

Uma melhoria concreta seria implementar **Best-Fit Decreasing com heap**:

```python
import heapq

# Heap de (espaço_disponivel_negado, numero_consultorio)
heap = []
for atend in normais:
    if heap and -heap[0][0] >= atend.duracao:
        espaco, num = heapq.heappop(heap)
        consultorios[num - 1].alocar(atend)
        heapq.heappush(heap, (espaco + atend.duracao, num))
    else:
        novo = Consultorio(numero=len(consultorios) + 1)
        novo.alocar(atend)
        consultorios.append(novo)
        heapq.heappush(heap, (-novo.tempo_disponivel, novo.numero))
```

Isso reduziria a complexidade de alocação de O(n²) para **O(n log n)**, com a
desvantagem de ser Best-Fit em vez de First-Fit (ligeiramente diferente na semântica).
Optei por não usar porque FFD com lista linear é mais simples de explicar e testar
unitariamente, e para os volumes esperados numa clínica (dezenas a centenas de
atendimentos por dia), O(n²) é absolutamente imperceptível.
