# RACIOCINIO.md — Clínica Veterinária

---

## Parte 1 — Modelagem do problema

### 1. Classificação do problema

Este problema é uma combinação de **escalonamento com janelas de tempo** (*scheduling with time windows*) e **empacotamento em múltiplos contêineres* (*bin packing*).

Características do enunciado que apoiam essa classificação:

- Cada consultório tem **sessões com horários fixos de início e fim** (08:00–11:30 e 13:30–18:00), o que introduz janelas de tempo rígidas — característica central do escalonamento.
- Os atendimentos têm **durações variadas** e precisam ser distribuídos entre consultórios de forma a respeitar a capacidade de cada sessão — característica do bin packing.
- O número de consultórios não é fixo: o programa deve minimizá-lo (ou pelo menos calculá-lo), o que é exatamente o objetivo do *bin packing* clássico: usar o menor número possível de "caixas".
- A regra da reunião de encerramento (deve começar *depois* das 17:00 e *antes* das 18:00) introduz uma **restrição de validade** na sessão da tarde, tornando o problema mais restrito do que um bin packing puro.

### 2. Semelhança com problemas clássicos

O problema mais parecido é o **Bin Packing Problem (BPP)**:

> Dado um conjunto de itens com pesos e um conjunto de caixas com capacidade fixa, distribua os itens nas caixas usando o menor número possível de caixas.

A analogia direta é:

| Problema clássico | Nosso problema |
|---|---|
| Itens com pesos | Atendimentos com durações em minutos |
| Caixas com capacidade | Sessões (manhã/tarde) com limite de tempo |
| Minimizar número de caixas | Minimizar número de consultórios |

A diferença principal é que cada consultório possui **dois contêineres encadeados** (manhã e tarde), com restrições de janela distintas — o que torna este problema uma variação do *Multiple Bin Packing* com restrições de tempo.

### 3. Estruturas de dados escolhidas

**`Atendimento`** — classe simples (POJO) com nome, duração e flag `expresso`.
- Escolha: encapsula bem os dados de cada entrada sem overhead desnecessário.
- Alternativa: usar um `record` do Java 16+, que seria mais conciso, mas menos didático.

**`Sessao`** — lista de atendimentos (`ArrayList<Atendimento>`) + lista paralela de horários de início (`ArrayList<int[]>`), com controle de `tempoAtual`.
- Escolha: `ArrayList` garante inserção O(1) amortizado e acesso por índice O(1), ideal para percorrer na impressão. A lista paralela de horários evita recalcular os tempos na impressão.
- Alternativa: usar um `LinkedHashMap<Integer, Atendimento>` (chave = horário) tornaria a impressão mais direta, mas complicaria a verificação de espaço disponível.

**`Consultorio`** — agrega dois objetos `Sessao` (manhã e tarde) e o número do consultório.
- Escolha: separação clara de responsabilidades — cada sessão gerencia seu próprio tempo e agenda.
- Alternativa: usar um único array de slots de minuto seria mais eficiente em memória, mas muito mais difícil de manter e imprimir.

**`List<Consultorio>`** — lista de todos os consultórios abertos, gerenciada pelo `Escalonador`.
- Escolha: `ArrayList` permite percorrer todos os consultórios na ordem de abertura, e adicionar novos ao final em O(1) amortizado.

---

## Parte 2 — Estratégia algorítmica

### 4. Algoritmo em linguagem natural (passo a passo)

1. **Leitura da entrada:** o programa lê o arquivo `atendimentos.txt` linha a linha. Cada linha é analisada: se termina com "expresso", a duração é fixada em 10 minutos; caso contrário, extrai-se o número antes de "min". O nome é o restante da linha.

2. **Ordenação decrescente:** antes de qualquer alocação, a lista de atendimentos é ordenada do mais longo para o mais curto. Isso é a heurística *First-Fit Decreasing* (FFD), que tende a produzir soluções melhores do que encaixar os itens na ordem original.

3. **Loop de alocação:** para cada atendimento (já ordenado):
   - Percorre todos os consultórios já abertos e tenta encaixá-lo na **sessão da manhã** do primeiro que tiver tempo disponível.
   - Se nenhuma manhã comportar, percorre novamente e tenta encaixar na **sessão da tarde** do primeiro que tiver tempo disponível sem violar o limite das 18:00.
   - Se ainda assim não houver espaço, **abre um novo consultório** e coloca o atendimento na sua manhã.

4. **Impressão:** percorre os consultórios em ordem e imprime cada sessão com os horários calculados, a higienização ao meio-dia e a reunião de encerramento ao final da tarde (garantindo que ela caia depois das 17:00).

### 5. Abordagem: gulosa (greedy)

A solução é **gulosa com heurística FFD (First-Fit Decreasing)**.

A decisão foi tomada por dois motivos:

- **Bin packing é NP-difícil**: não existe algoritmo de tempo polinomial que garanta a solução ótima (a não ser que P=NP). Para a escala do problema (dezenas a centenas de atendimentos), uma heurística eficiente é a abordagem prática.
- **FFD tem garantias teóricas**: é provado que FFD nunca usa mais de `11/9 * OPT + 6/9` caixas, onde OPT é o número ótimo. Na prática, costuma ser igual ou muito próximo do ótimo.

A alternativa seria usar programação dinâmica ou busca exaustiva (backtracking), mas ambas têm complexidade exponencial no pior caso.

### 6. Caso em que o algoritmo não encontra a solução ótima

Exemplo concreto com 4 atendimentos e consultórios com manhã de 210 minutos (08:00–11:30):

```
A: 120min
B: 110min
C: 100min
D: 90min
```

**FFD ordena: A(120), B(110), C(100), D(90)**

- Consultório 1, manhã: A(120) → resta 90min. B(110) não cabe. → Tarde.
- Consultório 1, tarde: B(110) → ok.
- Consultório 2, manhã: C(100) → resta 110min. D(90) cabe! → D na manhã 2.
- **Resultado: 2 consultórios.**

Neste caso FFD achou o ótimo. Mas considere:

```
A: 120min
B: 120min
C: 90min
D: 90min
```

**FFD: A(120), B(120), C(90), D(90)**

- Consultório 1 manhã: A(120), sobram 90min → C(90) cabe → C na manhã 1.
- Consultório 1 tarde: B(120) → ok. Sobram 150min → D(90) cabe → D na tarde 1.
- **Resultado: 1 consultório.**

Mas e se as restrições de tempo da tarde forçassem outro arranjo? Com uma restrição de reunião mais rígida, o algoritmo poderia usar 2 consultórios enquanto 1 seria suficiente com outra distribuição. FFD não faz *backtracking*, então uma decisão gulosa errada pode não ser desfeita.

### 7. Complexidade de tempo

- **Ordenação:** O(n log n) — domina.
- **Loop de alocação:** para cada um dos n atendimentos, percorremos todos os consultórios abertos. No pior caso, cada atendimento abre um novo consultório, chegando a n consultórios → O(n²) no pior caso.
- **Impressão:** O(n) — percorre cada atendimento uma vez.

**Complexidade total: O(n²)**, dominada pelo loop de alocação.

Na prática, o número de consultórios é muito menor que n (tipicamente O(√n) ou menos), tornando o comportamento médio muito mais próximo de O(n log n).

---

## Parte 3 — Decisões de implementação

### 8. Como o programa decide quantos consultórios abrir

O programa começa com zero consultórios. Só abre um novo quando o atendimento atual não cabe em **nenhuma sessão** (manhã ou tarde) de nenhum consultório já existente. Isso é a estratégia *First-Fit*: tenta encaixar no primeiro espaço disponível antes de criar espaço novo.

Critério de encaixe para a manhã: `tempoAtual + duração <= 690` (11:30 em minutos).
Critério de encaixe para a tarde: `tempoAtual + duração <= 1080` (18:00 em minutos, limite hard da reunião).

### 9. Como os atendimentos expressos são tratados

Atendimentos expressos são convertidos para **10 minutos** logo na leitura (`Parser`), e a flag `expresso` é mantida apenas para fins de exibição (imprime "expresso" em vez de "10min").

Essa abordagem foi escolhida porque simplifica o algoritmo de escalonamento: ele não precisa de nenhum tratamento especial para expressos — eles são apenas atendimentos curtos. A distinção visual é restaurada apenas na saída.

Alternativa descartada: tratar expressos como uma fila separada com lógica de encaixe prioritário — aumentaria a complexidade desnecessariamente.

### 10. Parte mais inteligente e parte que poderia melhorar

**Parte mais inteligente: a ordenação FFD antes da alocação (`Escalonador.java`)**

```java
ordenados.sort((a, b) -> b.getDuracaoMinutos() - a.getDuracaoMinutos());
```

Uma linha só, mas é o que transforma uma solução ingênua (que poderia abrir 5+ consultórios) em uma solução eficiente (3 consultórios para a entrada de teste). Colocar os maiores primeiro garante que os "itens difíceis" sejam alocados quando há mais espaço disponível, deixando os pequenos preencherem as lacunas restantes.

**Parte que poderia melhorar: a estratégia de alocação da tarde**

Atualmente, a tarde de um novo consultório pode ficar **completamente vazia** (como acontece com o consultório 3 na entrada de teste). O algoritmo preenche a manhã do consultório 3 com os atendimentos de 30 minutos que não cabiam em nenhuma outra manhã, mas não há mais atendimentos para sua tarde.

Uma melhoria seria implementar um **pós-processamento**: após a alocação inicial, redistribuir atendimentos da manhã de consultórios com tarde vazia para a tarde de consultórios com espaço disponível, potencialmente eliminando consultórios inteiros. Isso transformaria o algoritmo em uma heurística de duas fases, melhorando a compactação sem explosão de complexidade.
