# RACIOCÍNIO

Este documento explica, com minhas próprias palavras, o raciocínio por trás da
solução. Sigo a numeração das 10 perguntas do enunciado (algumas têm duas
partes — estrutura de dados e o "o que mudaria" na 3, e a parte inteligente +
a melhorável na 10 — totalizando os 12 pontos de discussão).

> Antes de tudo, **uma decisão de interpretação das regras** que vale para todo
> o resto: a reunião "começa depois das 17:00, mas antes das 18:00". Modelei a
> janela como **[17:00, 18:00)** — a reunião não começa antes das 17:00 (a tarde
> precisa ter pelo menos 210 min) e precisa ter começado antes das 18:00 (a
> tarde tem menos de 270 min). Tratei o limite das 17:00 como aceitável (a
> reunião pode começar exatamente às 17:00). É uma escolha consciente, isolada
> em constantes em [`clinica/regras.py`](clinica/regras.py); se o professor
> quiser "estritamente depois das 17:00", muda-se uma linha.

---

## Parte 1 — Modelagem do problema

### 1. Como classifiquei o problema

Classifico como um problema de **empacotamento (bin packing)** com um tempero de
**escalonamento por turnos (scheduling)**.

O que do enunciado sustenta isso:

- **Itens com "tamanho":** cada atendimento tem uma duração em minutos. Esse é o
  "peso" do item.
- **Recipientes de capacidade fixa:** cada sessão é uma janela de tempo limitada
  — a manhã vai das 08:00 às 11:30 (210 min) e a tarde das 13:30 até a reunião.
  São as "caixas".
- **Minimizar o número de caixas:** o enunciado diz explicitamente que o número
  de consultórios **não é fixo** e deve ser **calculado**. Querer usar o menor
  número possível de recipientes é exatamente o que define o bin packing.

O componente de **escalonamento** entra porque não basta empacotar: há horários
de início (08:00, 13:30) e, principalmente, a **tarde tem uma janela** — não pode
ficar curta demais (reunião antes das 17:00) nem longa demais (reunião depois das
18:00). Ou seja, a "caixa da tarde" tem um **mínimo e um máximo**, o que é uma
restrição de agendamento, não de empacotamento puro.

Não é um problema de busca em grafo, nem de otimização contínua: o espaço é
discreto e combinatório (cada atendimento vai inteiro para uma sessão).

### 2. Semelhança com problemas clássicos

O parente direto é o **Bin Packing Problem** (problema do empacotamento), que é
**NP-difícil**. Também é quase idêntico ao kata clássico de entrevistas
**"Conference Track Management"** (organizar palestras em trilhas com sessão da
manhã e da tarde, terminando a tempo de um evento de encerramento) — trocando
palestras por atendimentos, trilhas por consultórios e o evento por reunião, é o
mesmo problema.

Explicando a analogia do bin packing com minhas palavras: é como **uma mudança
de casa**. Tenho várias caixas, cada uma aguenta um limite de peso, e quero
levar todos os meus objetos usando o **menor número de caixas**. Aqui a "caixa"
é o tempo de uma sessão e o "peso" de cada objeto é a duração do atendimento.

A diferença para o bin packing de livro é a regra da tarde: a caixa da tarde tem
**peso mínimo** — não pode ir quase vazia, senão a reunião começaria cedo demais.
Há também parentesco com o **Problema da Partição** (dividir números em grupos de
soma parecida) e com a **Mochila** (escolher itens respeitando uma capacidade).

### 3. Estruturas de dados escolhidas

Modelei cada conceito do enunciado em uma classe própria
([`clinica/modelos.py`](clinica/modelos.py)):

- **`Atendimento`** → uma *dataclass* **imutável** (`frozen=True`) com `nome`,
  `duracao` e `expresso`.
  - *Por quê:* depois de lido do arquivo, um atendimento nunca muda — ele só é
    **movido** de uma sessão para outra. Imutável evita o bug de alguém alterar a
    duração por engano e ainda o torna **hasheável**, o que uso nos testes
    (`Counter` de atendimentos) para garantir que nenhum se perdeu ou duplicou.
  - *O que mudaria com outra escolha:* um `dict {"nome":..., "duracao":...}`
    funcionaria, mas sem garantia de campos nem autocompletar, e eu teria que
    decorar as chaves; uma tupla `(nome, dur)` seria compacta, porém ilegível
    (`a[1]` em vez de `a.duracao`).

- **`Sessao`** → um objeto com uma **lista ordenada** de atendimentos, mais
  `teto`, `minimo` e `inicio`.
  - *Por quê lista:* **a ordem importa**. A ordem de inserção é a ordem em que os
    atendimentos são impressos e é o que define os horários (08:00, 08:00+dur₁,
    08:00+dur₁+dur₂, ...). `append` é O(1).
  - *O que mudaria:* se eu guardasse só o **total de minutos** (sem a lista),
    economizaria memória, mas perderia *quais* atendimentos e em que *ordem* —
    e aí não conseguiria imprimir a agenda. Um *heap* por duração também não
    serve, porque a exibição é **cronológica**, não por tamanho.

- **`Consultorio`** → um objeto com exatamente **duas `Sessao`** (`manha`,
  `tarde`).
  - *Por quê:* espelha o domínio (1 consultório = 2 sessões) e impede, por
    construção, um consultório com 3 turnos por engano.
  - *O que mudaria:* poderia ser uma lista de sessões com um campo "turno", mas
    `manha`/`tarde` explícitos deixam o código mais legível.

- A **coleção de consultórios** é uma **lista** simples — a posição já é a
  numeração (1, 2, 3...).

Observação de desempenho: na hora de achar o "melhor encaixe" eu **varro a lista
de sessões**. Se eu usasse uma **fila de prioridade (heap)** ordenada por folga,
essa escolha cairia de O(nº de sessões) para O(log). Para o tamanho deste
problema, a lista é mais simples de ler e de defender; o heap valeria a pena só
com muitos consultórios.

---

## Parte 2 — Estratégia algorítmica

### 4. O algoritmo passo a passo (sem código)

Imagine que recebi a lista e preciso montar as agendas:

1. **Leio** cada linha e transformo em (nome, duração). `"expresso"` vira 10 min.
2. **Somo** a duração de tudo. Como um consultório, no melhor caso, comporta
   210 min de manhã + quase 270 de tarde (≈ 479 min úteis), divido o total por
   479 e arredondo para cima. Esse é o **palpite do número mínimo** de
   consultórios — para a lista oficial dá **3**.
3. **Abro** essa quantidade de consultórios (manhãs e tardes vazias).
4. **Ordeno** os atendimentos do **maior para o menor**. Itens grandes são os
   mais difíceis de encaixar; resolvê-los primeiro deixa os pequenos para ajuste
   fino no fim.
5. **Cuido primeiro das tardes.** Enquanto existir uma tarde com menos de 210
   minutos (senão a reunião começaria antes das 17:00), pego a **tarde mais
   vazia** e coloco nela o **maior atendimento que ainda cabe** sem passar de 270
   (senão a reunião passaria das 18:00). Repito até **toda** tarde estar dentro
   da janela [210, 270).
6. **Depois distribuo o resto.** Para cada atendimento restante, procuro a sessão
   (qualquer manhã, ou a folga de uma tarde) onde ele cabe deixando a **menor
   sobra** — o "melhor encaixe" (best-fit), para desperdiçar pouco tempo.
7. Se em algum momento um atendimento **não couber em lugar nenhum**, é sinal de
   que faltou espaço: **abro um consultório a mais** e refaço a montagem.
8. No fim, **confiro** que toda manhã ≤ 210 e toda tarde ∈ [210, 270) e
   **imprimo**: manhã a partir das 08:00, higienização fixa às 11:30, tarde a
   partir das 13:30 e a reunião no horário em que a tarde termina.

### 5. É gulosa, exata ou heurística?

É uma **heurística gulosa**.

- **Gulosa** porque, em cada passo, faço a escolha que parece melhor
  *localmente* (a tarde mais vazia recebe o maior item que cabe; o resto vai para
  o encaixe mais justo) e **nunca volto atrás**.
- **Heurística** porque essas regras de bom senso (maior-primeiro, melhor-encaixe,
  tarde-primeiro) funcionam muito bem na prática, mas **não provam** que o
  resultado é o ótimo global.

**Como cheguei a essa decisão:** o núcleo é bin packing, que é **NP-difícil**.
Uma solução **exata** (testar todas as combinações, ou usar programação inteira /
backtracking completo) cresce de forma explosiva com o número de atendimentos —
seria exagero para a agenda de uma clínica e para um desafio de nível júnior. O
ganho de, no pior caso, economizar 1 consultório raríssimas vezes não compensa a
complexidade. Heurísticas gulosas da família *"decreasing-fit"* são o padrão da
indústria para empacotamento justamente porque são **rápidas** e ficam **muito
perto do ótimo**. Por isso optei por gulosa.

### 6. Entrada em que meu algoritmo NÃO acha a melhor solução

Sim, existe — e eu **encontrei uma por busca exaustiva** comparando meu resultado
com um solucionador exato (força bruta) para listas pequenas.

**Entrada:** cinco atendimentos com durações `45, 90, 90, 120, 120` (todas
durações realistas de clínica). Total = 465 min.

- **O ótimo é 1 consultório:**
  - Tarde: `120 + 90 + 45 = 255` → reunião às **17:45** (∈ [17:00, 18:00) ✔)
  - Manhã: `120 + 90 = 210` → termina exatamente às **11:30** ✔
- **Meu algoritmo usa 2 consultórios.** Por quê (rastreei o passo a passo):
  1. Na Fase 1, ordeno decrescente `[120, 120, 90, 90, 45]` e encho a tarde com
     os **maiores primeiro**: `120 + 120 = 240` (já passou de 210, paro).
  2. Sobram `90, 90, 45` para a manhã. Mas `90 + 90 + 45 = 225 > 210`: o `45`
     **não cabe em manhã nenhuma**.
  3. Como nada mais encaixa, meu algoritmo conclui que 1 consultório não basta e
     **abre o segundo**.

O erro é típico de algoritmo guloso: ao colocar `120 + 120` na tarde "porque eram
os maiores", ele **fechou a porta** para a combinação `120 + 90 + 45 = 255`, que
era a única que deixava a manhã com exatos `120 + 90 = 210`. Um solucionador
exato testaria essa combinação "menos óbvia"; o guloso, não, porque não volta
atrás. Esse é exatamente o preço que aceitei pagar na pergunta 5.

(Curiosidade que orientou meu desenho: um guloso **ingênuo**, que enchesse os
consultórios da esquerda para a direita, falharia já na **lista oficial** —
deixaria o consultório 3 com a **tarde vazia**. Foi por isso que inverti a ordem
e passei a **encher as tardes primeiro**.)

### 7. Complexidade de tempo aproximada

Seja `n` o número de atendimentos.

- **Leitura/parse:** O(n).
- **Ordenação** (maior → menor): **O(n log n)**.
- **Fase 1:** cada repetição coloca **um** atendimento, então roda no máximo `n`
  vezes; em cada uma ela ordena as tardes abaixo do mínimo (O(k log k)) e varre os
  pendentes (O(n)) atrás do maior que cabe. Isso dá **O(n²)** no pior caso (com
  `k` ≤ `n`).
- **Fase 2:** para cada um dos ≤ `n` atendimentos, varro as `2k` sessões → **O(n·k)**.
- **Reabertura:** se faltar espaço, tento `k`, `k+1`, ... O número de tentativas é
  pequeno (na prática 0 ou 1), mas no pior caso teórico é O(n).

Juntando: **na prática**, com o número de consultórios `k` pequeno em relação a
`n`, o custo é dominado pela **ordenação, ≈ O(n log n)** (mais um termo O(n·k) de
distribuição). **No pior caso teórico** (muitas reaberturas e `k` da ordem de
`n`), fica polinomial — algo como O(n³). O importante: é **polinomial**, nada de
explosão combinatória, que é justamente o que eu queria ao escolher a heurística.

---

## Parte 3 — Decisões de implementação

### 8. Como o programa decide quantos consultórios abrir

O critério está em
[`numero_minimo_consultorios`](clinica/escalonador.py) + o laço de
[`organizar`](clinica/escalonador.py):

1. Calculo um **limite inferior teórico**: a maior quantidade de minutos que
   *um* consultório aguenta é `210` (manhã) `+ 269` (tarde, que precisa ser
   `< 270`) `= 479`. Logo, nem que todos ficassem cheios, eu precisaria de pelo
   menos `teto(total / 479)` consultórios. Para a lista oficial:
   `teto(1095 / 479) = 3`.
2. Começo com esse número e **tento montar** a agenda. Se tudo couber e todas as
   regras forem respeitadas, pronto.
3. Se algum atendimento **não couber**, abro **um consultório a mais** e tento de
   novo, subindo de um em um.

Ou seja, **abro o menor número que eu consigo provar necessário pela capacidade**
e só aumento quando a montagem falha. Para a entrada oficial, isso resulta em
**3 consultórios** (e os testes verificam exatamente esse número).

### 9. Como tratei os atendimentos expressos

Tratei o expresso como **um atendimento normal de 10 minutos** — a constante
`EXPRESSO_MIN = 10` em [`clinica/regras.py`](clinica/regras.py). O parser
([`clinica/parser.py`](clinica/parser.py)) reconhece o token final `expresso`,
atribui duração 10 e marca a flag `expresso=True` (que serve só para **imprimir**
"expresso" em vez de "10min", preservando o rótulo original do enunciado).

**Por que essa abordagem:** depois de virar "10 minutos", o expresso participa do
empacotamento **igual a todos os outros**, sem nenhum caso especial no algoritmo.
Isso mantém o código simples (uma regra a menos para errar). E tem um bônus: como
ordeno do maior para o menor, os expressos ficam **no fim da fila** e acabam
sendo usados como **peças de ajuste fino** — são pequenos o suficiente para
caber nas últimas frestas das sessões e "fechar a conta" sem estourar os limites.
Dá para ver isso na saída oficial: o `Microchipagem expresso` e a
`Aplicação de vacina antirrábica expresso` entram no finalzinho das tardes.

### 10. A parte mais inteligente e a que pode melhorar

**Parte mais inteligente — encher as tardes primeiro (Fase 1,
[`clinica/escalonador.py:74-94`](clinica/escalonador.py)).**
A sacada não é óbvia: o instinto seria preencher cada consultório por completo
antes de passar ao próximo. Eu testei isso no papel e descobri que, na **própria
entrada oficial**, sobraria pouco para o último consultório e a **tarde dele
ficaria vazia** — violando a regra da reunião. Inverter a lógica e **garantir o
mínimo de cada tarde antes de mexer nas manhãs** resolve isso de forma elegante:
como a manhã *não* tem mínimo (pode até ficar vazia), é seguro deixá-la por
último; já a tarde, que tem janela obrigatória, é a parte "frágil" e merece ser
resolvida primeiro. Escolher sempre a **tarde mais vazia** ainda equilibra a carga
entre os consultórios.

**Parte que pode melhorar — a falta de "voltar atrás" e o desequilíbrio das
manhãs.**
Dois pontos ligados:
1. Como mostrei na pergunta 6, a Fase 1 **se compromete** com os maiores itens na
   tarde e nunca reconsidera. Bastaria uma etapa de **troca local** (ex.: se a
   manhã estoura por pouco, tentar trocar um item da tarde por um menor para
   liberar espaço) para resolver casos como `[45, 90, 90, 120, 120]` sem abrir um
   consultório extra. Não implementei para manter a solução simples e honesta
   sobre seus limites, mas é a primeira melhoria que eu faria.
2. Na saída oficial, o **consultório 3 fica com a manhã vazia**. Isso é
   *válido* (a manhã não tem mínimo), mas é feio. Um passo de **rebalanceamento**
   no fim — espalhar os atendimentos da manhã mais uniformemente — deixaria as
   agendas mais "humanas", sem mudar a correção.

Um detalhe menor também melhorável: a busca do melhor encaixe varre todas as
sessões a cada item (O(nº de sessões)); com muitos consultórios, valeria trocar
por uma fila de prioridade por folga.
