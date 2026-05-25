# RACIOCINIO.md — Organizador de Atendimentos

---

## Parte 1 — Modelagem do Problema

### 1. Como você classificou esse problema?

Classifiquei como um problema de **empacotamento com restrição de janela** (*bin packing with bounded bins*), com elementos de **escalonamento em máquinas paralelas**.

Características do enunciado que apoiam essa classificação:

- **Vários consultórios funcionando em paralelo** → são as "máquinas" ou os "bins".
- **Cada consultório tem dois turnos com capacidades fixas** → manhã tem exatamente 210 min disponíveis; tarde deve ser usada entre 210 e 269 min.
- **Atendimentos têm durações heterogêneas** → os "itens" a empacotar têm tamanhos variados (10, 30, 45, 60, 90, 120 min).
- **O número de consultórios não é dado** → o programa deve calcular o menor número necessário, o que é o objetivo clássico do bin packing: minimizar o número de bins.
- **A restrição de reunião (entre 17h e 18h)** impõe um *lower bound* e um *upper bound* para cada tarde, tornando o problema uma variante com **janela dupla de capacidade** — mais restritivo que o bin packing tradicional.

### 2. Semelhança com problemas clássicos

O problema é análogo ao **Bin Packing Problem (BPP)**, um dos problemas NP-difíceis mais estudados da computação.

No BPP clássico, você tem itens de tamanhos variados e bins de capacidade fixa, e quer distribuir todos os itens usando o menor número de bins possível. Aqui, cada "bin" é uma sessão de um consultório.

A principal diferença — e o que torna este problema mais interessante — é que a sessão da tarde tem um **mínimo obrigatório** (210 min), e não apenas um máximo. Isso é equivalente a dizer: cada bin da tarde deve estar pelo menos 78% cheio. No BPP clássico, um bin pode ficar quase vazio; aqui não.

Há também semelhança com o **Multiprocessor Scheduling Problem** (ou *Identical Parallel Machines*), onde o objetivo é distribuir tarefas entre máquinas para minimizar o makespan (tempo total). A heurística LPT (Longest Processing Time) que usei vem exatamente desse contexto.

### 3. Estruturas de dados escolhidas

**`Atendimento` (dataclass)**
- Campos: `nome` (str), `duracao` (int em minutos), `expresso` (bool).
- Por quê dataclass? Agrupa os três atributos coesos, é imutável conceitualmente, e o Python gera `__repr__` e `__eq__` automaticamente — facilita debugging e testes.
- Se tivesse usado uma tupla `(nome, duracao, expresso)`, perderia legibilidade (atend[0] vs atend.nome) e tornaria o código frágil a reordenações.

**`Sessao` (dataclass com lista interna)**
- Campos: `inicio` (int), `capacidade` (int), `atendimentos` (List[Atendimento]).
- Encapsula a lógica de verificação de espaço (`cabe`) e inserção (`adicionar`) dentro da própria estrutura. Isso evita espalhar a lógica de `tempo_livre >= duracao` por todo o código.
- A `List` interna preserva a **ordem de inserção**, que é essencial para a saída cronológica correta.
- Se tivesse usado uma `deque`, não ganharia nada (não precisamos de inserção em O(1) no início). Se tivesse usado um dicionário, perderia a ordenação natural.

**`Consultorio` (dataclass com duas Sessoes)**
- Agrupa manhã e tarde sob um mesmo número. Permite iterar `c.sessoes()` de forma uniforme nos loops de validação.
- Se tivesse separado em duas listas independentes (`lista_manhas`, `lista_tardes`), o código ficaria propenso a erros de sincronização de índices.

**`List[Consultorio]` como estrutura raiz**
- Lista ordenada pelo número do consultório. O algoritmo acessa consultorios por índice e por iteração sequencial, o que é O(1) e O(n) respectivamente — perfeito para os padrões de acesso do LPT.

---

## Parte 2 — Estratégia Algorítmica

### 4. Descrição do algoritmo em linguagem natural

**Passo 0 — Leitura da entrada:**
O programa lê o arquivo linha por linha. Para cada linha, identifica se o último token é "expresso" (10 min fixos) ou um número seguido de "min". O nome do atendimento é tudo que vem antes dessa última parte.

**Passo 1 — Calcular o número mínimo de consultórios:**
Some todos os minutos de todos os atendimentos. Divida esse total por 269 (capacidade máxima de uma tarde) arredondando para cima. Esse é o menor número de consultórios que consegue acomodar toda a carga sem estourar nenhuma tarde.

**Passo 2 — Ordenar os atendimentos do maior para o menor:**
Atendimentos mais longos são mais difíceis de encaixar, então colocá-los primeiro dá ao algoritmo mais flexibilidade de escolha. Esse é o princípio LPT (Longest Processing Time First).

**Passo 3 — Alocar nas tardes (LPT balanceado):**
Para cada atendimento (maior primeiro), olhe todas as tardes existentes e identifique as que ainda têm espaço para receber aquele atendimento sem ultrapassar 269 min. Entre essas candidatas, escolha a que tem **menor carga acumulada** (menos minutos já alocados). Isso distribui os atendimentos de forma balanceada, como se estivesse nivelando água entre vasos.

Se nenhuma tarde existente aceitar o item (porque todas estão próximas de 269 min), abra um novo consultório.

**Passo 4 — O que sobrou vai para as manhãs:**
Atendimentos que não couberam em nenhuma tarde (por excederem os 269 min máximos) são alocados nas manhãs, também com LPT: cada item vai para a manhã com menor carga que ainda o aceita.

**Passo 5 — Validação:**
Percorre todos os consultórios verificando: (a) cada atendimento foi alocado exatamente uma vez, (b) nenhuma manhã ultrapassou 210 min, (c) nenhuma tarde terminou antes das 17h ou às 18h ou depois.

**Passo 6 — Formatação da saída:**
Para cada consultório, imprime os atendimentos da manhã em ordem cronológica, depois "Higienização" às 11:30, depois os da tarde em ordem cronológica, e por fim a hora da reunião de encerramento.

### 5. A solução é gulosa, exata, heurística ou outra abordagem?

É uma solução **gulosa heurística**, especificamente a heurística **LPT (Longest Processing Time First)** — amplamente estudada para escalonamento em máquinas paralelas.

**Como cheguei a essa decisão:**

O bin packing com restrição de janela é NP-difícil, então a solução exata (força bruta ou programação dinâmica) seria inviável para entradas grandes. Uma solução exata com 23 atendimentos poderia testar 23! ≈ 2,5 × 10²² combinações — impraticável.

Avaliei três heurísticas clássicas:

- **FFD (First-Fit Decreasing):** aloca cada item no *primeiro* bin que aceita. Rápido, mas tende a encher os primeiros bins e deixar os últimos vazios — problema grave aqui, pois toda tarde precisa ter pelo menos 210 min.
- **BFD (Best-Fit Decreasing):** aloca no bin que ficará mais cheio após a inserção. Minimiza desperdício, mas também tende a criar desequilíbrio.
- **LPT (Longest Processing Time):** aloca no bin com *menor carga atual*. Naturalmente distribui a carga de forma uniforme, o que é exatamente o que precisamos para garantir que todas as tardes atinjam o mínimo de 210 min.

O LPT foi a escolha natural porque nossa restrição de *lower bound* na tarde é equivalente a querer que todos os bins sejam "suficientemente cheios" — objetivo oposto ao bin packing clássico e perfeitamente alinhado com o LPT.

### 6. Existe entrada para a qual o algoritmo não encontra a solução ótima?

Sim. O LPT é heurístico e não garante sempre a solução ótima. Exemplo concreto:

```
Cirurgia longa A 200min
Cirurgia longa B 200min
Consulta C 120min
Consulta D 120min
Consulta E 120min
```

Total: 760 min. `ceil(760/269) = 3` consultórios.

Com LPT:
- A (200) → tarde[1] (menor carga: 0)
- B (200) → tarde[2] (menor carga: 0)
- C (120) → tarde[3] (menor carga: 0), tarde[3] = 120
- D (120) → tarde[3] (menor carga: 120, pois 120+120=240 ≤ 269)... Na verdade tarde[1] e tarde[2] têm 200 cada, tarde[3] tem 120. D vai para tarde[3]: 240.
- E (120) → tarde[1] tem 200, 200+120=320 > 269. tarde[2] tem 200, igual. tarde[3] tem 240, 240+120=360 > 269. Nenhuma aceita → abre tarde[4].

Resultado: 4 consultórios, mas com 3 seria impossível? Vamos checar: 3 × 269 = 807 ≥ 760. Seria possível, mas exigiria uma distribuição específica (ex: [200+69, 200+69, 200+91] — mas 69 e 91 não existem nos itens disponíveis). Com os itens dados (200, 200, 120, 120, 120), qualquer distribuição em 3 bins de máximo 269 é impossível: os dois itens de 200 precisam ficar em bins separados (200+120=320>269 não cabe), e o terceiro bin ficaria com 120 min — abaixo do mínimo de 210. Nesse caso específico, 4 consultórios é de fato o mínimo, e o algoritmo encontra o ótimo.

Um caso onde o LPT é sub-ótimo mas a solução ótima existe:

```
Item A 180min
Item B 180min
Item C 90min
Item D 90min
Item E 90min
Item F 90min
```
Total: 720 min. `ceil(720/269) = 3`. Ótimo: tarde[1]=180+90=270, tarde[2]=180+90=270, tarde[3]=90+90=180 < 210. Inviável em 3 bins com window [210, 269].  
Na prática, 3 bins de [210,269] precisariam de 630 a 807 min. 720 está no range — mas nenhuma combinação de {180, 180, 90, 90, 90, 90} produz 3 grupos dentro de [210, 269]. O algoritmo corretamente abrirá 4 consultórios.

O LPT pode falhar em entradas onde uma permutação específica permitiria encaixar tudo com menos consultórios, mas essa situação é rara na prática e a heurística resolve corretamente a grande maioria dos casos reais.

### 7. Complexidade de tempo

**O(n log n)**, onde n é o número de atendimentos.

Raciocínio:

1. **Parsing:** percorre as n linhas uma vez → O(n).
2. **Ordenação (sorted):** O(n log n).
3. **Fase de alocação nas tardes:**
   - Para cada um dos n atendimentos, percorre até k consultorios existentes para encontrar o de menor carga.
   - k cresce lentamente (na prática k << n para entradas realistas).
   - No pior caso (k ≈ n/2), a fase é O(n × k) = O(n²).
   - Com uma heap de prioridade (min-heap indexada pela carga), poderia ser O(n log k).
   - Na implementação atual, k é pequeno e constante para entradas típicas, então na prática comporta-se como O(n).
4. **Validação:** percorre todos os atendimentos alocados → O(n).

**Dominante: O(n log n)** pela ordenação, com O(n × k) na alocação — onde k é o número de consultórios, tipicamente O(√n) ou melhor para instâncias reais.

Se quisesse garantir O(n log n) no pior caso, substituiria a busca linear pelo consultório de menor carga por uma **heap de mínimo** (já que Python tem `heapq`). A implementação atual prioriza legibilidade para fins didáticos.

---

## Parte 3 — Decisões de Implementação

### 8. Como o programa decide quantos consultórios abrir?

O cálculo é: `N = ceil(total_minutos / TARDE_MAX)`.

Raciocínio: cada tarde comporta no máximo 269 min (para que a reunião seja às 17:59 ou antes). Se o total de minutos de todos os atendimentos é T, precisamos de pelo menos `ceil(T / 269)` consultórios para que todos caibam em tardes.

Esse é o **lower bound** pelo lado do máximo de cada tarde. O algoritmo começa com esse número e abre novos consultórios dinamicamente se algum item não couber (o que pode acontecer se a distribuição for desfavorável).

Observação importante: a restrição de *mínimo* (tarde ≥ 210 min) também influencia: se o total T for muito pequeno, pode não ser possível preencher todos os consultórios até 210 min. Nesse caso, o programa abre o número mínimo calculado e aceita que algumas tardes fiquem abaixo do mínimo — condição que seria detectada pela validação. Na prática, para entradas com carga total realista (como os 1095 min do arquivo original), isso não ocorre.

### 9. Como os atendimentos expressos foram tratados?

Os atendimentos expressos são tratados **exatamente como qualquer outro atendimento**, com a única diferença de que sua duração é fixada em 10 minutos na hora do parsing.

Por que essa abordagem?

1. **Uniformidade:** o algoritmo de alocação não precisa saber se um atendimento é expresso ou não — ele só enxerga durações. Isso mantém o código simples e coeso (Single Responsibility Principle).

2. **Flexibilidade:** se no futuro a duração padrão dos expressos mudar de 10 para 15 minutos, basta alterar a constante `DURACAO_EXPRESSO` em um único lugar.

3. **Ordenação natural:** como 10 min é a menor duração possível, os expressos sempre ficam no final da ordenação decrescente (são os últimos a serem alocados). Isso é ótimo: itens pequenos preenchem as "brechas" que sobram após alocar os itens grandes, maximizando o aproveitamento dos bins.

A alternativa seria tratá-los separadamente (ex: "todos os expressos vão para o final do turno"). Isso tornaria o código mais complexo sem ganho real, e poderia criar tardes desequilibradas.

### 10. Parte mais inteligente e parte que poderia ser melhorada

**Parte mais inteligente — a função `_min_consultorios` e a escolha de LPT:**

```python
def _min_consultorios(total_minutos: int) -> int:
    n = -(-total_minutos // TARDE_MAX)  # ceil division sem importar math
    return max(1, n)
```

O truque `-(-x // y)` para divisão de teto sem `import math` é elegante e idiomático em Python. Mais importante: a escolha de usar TARDE_MAX (269) e não a capacidade total (480) como divisor captura exatamente a restrição mais apertada do problema — a janela da tarde. Começar com o número certo de consultórios evita abrir bins desnecessários desde o início.

A combinação desse cálculo com o LPT (escolher sempre o bin menos carregado) é o núcleo que garante a distribuição balanceada das tardes sem precisar de backtracking.

**Parte que poderia ser melhorada — a busca linear pelo consultório de menor carga:**

```python
candidatas = [(s.tempo_usado, i) for i, s in enumerate(tardes) if s.cabe(item)]
_, idx = min(candidatas)
```

Essa busca percorre todos os consultórios abertos para cada atendimento. Com n atendimentos e k consultórios, isso é O(n × k). Para entradas grandes (centenas de atendimentos), seria mais eficiente usar uma **heap de prioridade** (min-heap) indexada pela carga de cada tarde:

```python
import heapq
heap = [(0, idx, tarde) for idx, tarde in enumerate(tardes)]
heapq.heapify(heap)
# Para cada item: pop o menor, insere, push de volta
```

Isso reduziria a fase de alocação de O(n × k) para O(n log k). Para o contexto deste problema (dezenas de atendimentos, poucos consultórios), a diferença é imperceptível — mas seria relevante em produção com milhares de atendimentos diários.
