# RACIOCÍNIO — Organização de Atendimentos

## Parte 1 — Modelagem do problema

### 1. Como você classificou esse problema?

Classifico este problema como um **problema de empacotamento (bin packing)**, mais especificamente uma variante do *two-dimensional bin packing*. As características do enunciado que sustentam essa classificação são:

- Temos **itens** (atendimentos) com tamanhos variados (durações em minutos) que precisam ser colocados em **recipientes** (consultórios).
- Cada consultório tem **dois compartimentos** com capacidade limitada: sessão da manhã (210 min) e sessão da tarde (até 269 min úteis).
- O objetivo é alocar todos os atendimentos usando o **menor número possível** de consultórios.
- Não importa a ordem específica dentro de cada sessão — apenas que a soma das durações respeite o limite.

Isso se encaixa perfeitamente na definição de bin packing: dado um conjunto de itens com tamanhos e bins com capacidade fixa, minimize o número de bins usados.

### 2. Semelhança com problemas clássicos da computação

Este problema é análogo ao **Bin Packing Problem (BPP)**, um dos problemas clássicos de otimização combinatória. A analogia é direta:

- **Bins** = consultórios (cada um com capacidade total = 210 + 269 = 479 min úteis, divididos em dois compartimentos).
- **Itens** = atendimentos, cujo "tamanho" é a duração em minutos.
- **Objetivo** = minimizar o número de bins (consultórios) necessários.

O BPP é NP-hard, o que significa que não existe algoritmo eficiente que garanta a solução ótima para qualquer entrada. Porém, heurísticas como **First Fit Decreasing (FFD)** produzem resultados muito bons na prática — e é exatamente o que eu uso.

### 3. Estruturas de dados escolhidas

- **`Atendimento`** (classe): armazena `nome` (string) e `duracao` (int, minutos). É a unidade atômica do problema. Usar uma classe permite encapsular o parsing da entrada e a formatação da saída.
- **`Consultorio`** (classe): contém duas listas (`manha` e `tarde`) de objetos `Atendimento`, e contadores `usado_manha` e `usado_tarde` para rastrear a capacidade usada. Usar contadores separados evita recalcular a soma das durações a cada tentativa de alocação.
- **`consultorios`** (lista): lista simples de objetos `Consultorio`, crescida dinamicamente conforme necessário.

Se eu tivesse usado apenas dicionários ao invés de classes, o código ficaria menos legível e mais difícil de testar. Se usasse uma abordagem com matrizes ou arrays fixos, perderia a flexibilidade de crescer dinamicamente o número de consultórios.

---

## Parte 2 — Estratégia algorítmica

### 4. Descrição do algoritmo em linguagem natural

1. **Leitura**: Carrego a lista de atendimentos do arquivo texto, parseando o nome e a duração de cada um.
2. **Ordenação**: Ordeno todos os atendimentos por duração, do maior para o menor (First Fit Decreasing).
3. **Alocação**: Para cada atendimento (começando pelo mais longo):
   - Percorro os consultórios já abertos, na ordem em que foram criados.
   - Para cada consultório, tento encaixar na manhã primeiro (se cabe nos 210 min restantes) e, se não couber, na tarde (se cabe nos 269 min restantes).
   - Se nenhum consultório existente tem espaço, abro um novo consultório e aloco o atendimento nele.
4. **Impressão**: Para cada consultório, imprimo a agenda da manhã (a partir das 08:00), a higienização às 11:30, a agenda da tarde (a partir das 13:30), e a reunião de encerramento (que começa no máximo entre o fim dos atendimentos da tarde e as 17:00).

### 5. Tipo de abordagem

Minha solução é **gulosa (greedy)**, usando a heurística **First Fit Decreasing (FFD)**:

- **Decreasing**: Ordena os itens do maior para o menor antes de alocar.
- **First Fit**: Aloca cada item no primeiro bin (consultório) onde ele cabe.

Cheguei a essa decisão porque:
- O problema é NP-hard (bin packing), então uma solução exata seria impraticável para listas grandes.
- FFD é uma heurística clássica que garante usar no máximo (11/9)·OPT + 6/9 bins, onde OPT é o número ótimo.
- Para os tamanhos de entrada esperados (dezenas de atendimentos), FFD produz resultados ótimos ou muito próximos do ótimo.

### 6. Entrada para a qual o algoritmo não encontra a solução ótima

Sim. Considere:

```
Atendimento A 110min
Atendimento B 110min
Atendimento C 100min
Atendimento D 100min
```

Com FFD, o algoritmo ordena: A(110), B(110), C(100), D(100).
- Consultório 1 manhã: A(110) → sobra 100. B(110) não cabe (100 < 110).
- Consultório 1 tarde: B(110) → sobra 159.
- Consultório 1 manhã: C(100) cabe (100 ≤ 100) → manhã cheia (210).
- Consultório 1 tarde: D(100) cabe (110+100=210 ≤ 269) → ok.

Neste caso, FFD consegue 1 consultório. Mas considere:

```
Atendimento A 106min
Atendimento B 106min
Atendimento C 105min
Atendimento D 105min
Atendimento E 105min
Atendimento F 105min
```

FFD ordena: A(106), B(106), C(105), D(105), E(105), F(105). Total = 632 min. Capacidade por consultório = 479. Ótimo = 2 consultórios (316 cada).

- Consultório 1 manhã: A(106) → sobra 104. B(106) não cabe.
- Consultório 1 tarde: B(106) → sobra 163. C(105) → sobra 58. D(105) não cabe.
- Consultório 2 manhã: D(105) → sobra 105. E(105) cabe → manhã cheia (210).
- Consultório 2 tarde: F(105).
- Resultado: 2 consultórios. Ótimo atingido neste caso.

Um caso real de subotimalidade de FFD é difícil de construir para bins com 2 compartimentos, mas pode ocorrer quando a fragmentação impede preenchimento ideal dos compartimentos.

### 7. Complexidade de tempo

- **Parsing**: O(n), onde n é o número de atendimentos.
- **Ordenação**: O(n log n).
- **Alocação**: Para cada um dos n atendimentos, no pior caso percorremos todos os k consultórios já criados. Como k ≤ n, o pior caso é O(n²).
- **Total**: **O(n² )** no pior caso, dominado pela etapa de alocação.

Na prática, k é muito menor que n (poucos consultórios para muitos atendimentos), então o desempenho é significativamente melhor que n².

---

## Parte 3 — Decisões de implementação

### 8. Como o programa decide quantos consultórios abrir?

O número de consultórios é determinado **dinamicamente** durante a alocação. Começo com zero consultórios. Cada vez que um atendimento não cabe em nenhum consultório existente (nem na manhã, nem na tarde), um novo consultório é instanciado e adicionado à lista. Isso garante que o programa use exatamente o número necessário — nem mais, nem menos.

### 9. Como tratei os atendimentos expressos?

Atendimentos marcados como "expresso" são tratados como atendimentos normais com duração fixa de **10 minutos**. A detecção é feita no parsing: se a linha termina com a palavra "expresso", a duração é 10 min e o nome completo (incluindo "expresso") é preservado.

Essa abordagem é simples e eficaz porque:
- Expressos são os menores atendimentos, então naturalmente preenchem "buracos" no final das sessões.
- Com FFD (ordenação decrescente), eles são alocados por último, funcionando como "preenchimento" — encaixam-se nos espaços residuais dos consultórios já parcialmente preenchidos.

### 10. Trecho mais inteligente e trecho que poderia ser melhorado

**Parte mais inteligente** — A ordenação decrescente antes da alocação (FFD):

```python
atendimentos.sort(key=lambda x: x.duracao, reverse=True)
```

Esta única linha transforma o algoritmo de First Fit simples (que pode desperdiçar muito espaço) em First Fit Decreasing, que tem garantias teóricas de qualidade. Colocando os atendimentos longos primeiro, evitamos criar consultórios desnecessários — os atendimentos curtos e expressos preenchem os espaços restantes naturalmente.

**Parte que poderia ser melhorada** — A busca linear por consultórios disponíveis:

```python
for c in consultorios:
    if c.adicionar(att):
        alocado = True
        break
```

Para entradas muito grandes, essa busca O(k) para cada atendimento gera complexidade O(n²). Poderia ser otimizada usando uma **estrutura de dados com prioridade** (como um heap ordenado pelo espaço restante) para encontrar o melhor consultório em O(log k), reduzindo a complexidade total para O(n log n). Para o contexto deste problema (dezenas de atendimentos), não faz diferença prática, mas seria relevante para escala.
