# RACIOCINIO.md

## Parte 1 — Modelagem do problema

### 1. Como você classificou esse problema?

Classifiquei como um problema de **empacotamento** (*Bin Packing*).

As características do enunciado que apoiam isso são diretas: cada sessão (manhã ou tarde de um consultório) tem uma capacidade máxima em minutos — 210 para manhã, 269 para tarde — e cada atendimento tem um "tamanho" que é sua duração. O objetivo é distribuir todos os atendimentos nessas sessões sem ultrapassar nenhuma capacidade, usando o menor número de consultórios possível.

É empacotamento e não escalonamento porque não existe dependência entre os atendimentos (um não precisa terminar pra outro começar, exceto dentro da mesma sessão), e não existe prioridade ou prazo por atendimento. O único critério é caber dentro do limite de tempo da sessão.

---

### 2. Semelhança com problemas clássicos

O problema é uma instância direta do **Bin Packing Problem**, um dos problemas clássicos de otimização combinatória da ciência da computação.

A analogia é precisa: os "bins" (caixas) são as sessões da clínica, cada uma com sua capacidade em minutos. Os "itens" são os atendimentos, cada um com seu tamanho em minutos. O objetivo original do Bin Packing é minimizar o número de caixas usadas — aqui, minimizar o número de consultórios abertos.

O Bin Packing é NP-difícil, o que significa que não existe algoritmo eficiente conhecido que garanta sempre a solução ótima. Por isso a abordagem prática é usar heurísticas como o FFD, que não são perfeitas mas chegam perto com custo computacional razoável.

---

### 3. Estruturas de dados escolhidas

**`Atendimento`** é uma struct simples com três campos: nome (string), duração (int) e label (string com o valor original, como "90min" ou "expresso"). Escolhi struct porque os dados são fixos após o parse — não muda, não precisa de comportamento, só carrega informação. Uma alternativa seria um map, mas perderia a tipagem e tornaria o código menos legível.

**`Sessao`** é uma struct com a hora de início, capacidade máxima, lista de atendimentos e tempo já ocupado. O tempo ocupado é mantido como campo separado para que a verificação `Cabe` seja O(1) — sem precisar somar a lista toda a cada consulta. Usei ponteiro (`*Sessao`) para que as modificações durante a alocação reflitam diretamente na estrutura sem cópias acidentais.

**`Consultorio`** agrupa dois ponteiros de `Sessao` (manhã e tarde) com um ID numérico. Poderia ter usado um slice de sessões em vez de dois campos nomeados, mas dois campos explícitos tornam o código mais legível — `c.Manha` é mais claro que `c.Sessoes[0]`.

A lista de consultórios é um slice de ponteiros (`[]*Consultorio`), crescendo dinamicamente conforme necessário. Um array de tamanho fixo não funcionaria porque o número de consultórios é calculado em tempo de execução.

---

## Parte 2 — Estratégia algorítmica

### 4. O algoritmo passo a passo

Primeiro, todos os atendimentos são lidos do arquivo e parseados. Depois o algoritmo faz o seguinte:

**Passo 1:** Ordena a lista de atendimentos do maior para o menor em duração. Uma cirurgia de 120 minutos vem antes de uma consulta de 30 minutos.

**Passo 2:** Para cada atendimento na lista ordenada, tenta encaixá-lo em algum lugar já existente — primeiro percorre todas as manhãs de todos os consultórios já abertos; se nenhuma tiver espaço, percorre todas as tardes.

**Passo 3:** Se o atendimento não couber em nenhuma sessão existente, abre um consultório novo e coloca o atendimento na manhã dele. Se for grande demais até para a manhã (mais de 210 minutos), vai para a tarde do novo consultório.

**Passo 4:** Após todos os atendimentos alocados, percorre os consultórios e imprime os horários calculados sequencialmente, a higienização fixa às 11:30 (se a manhã tiver atendimentos) e a reunião de encerramento no horário em que a tarde terminar — ou às 17:00, o que vier depois.

---

### 5. Gulosa, exata ou heurística?

A solução é **gulosa e heurística**.

É **gulosa** porque toma decisões locais e irreversíveis: ao alocar um atendimento na primeira sessão que couber, o algoritmo não volta atrás para reorganizar. Não existe backtracking.

É **heurística** porque não garante a solução ótima em todos os casos — ela encontra uma solução boa e válida, mas não necessariamente a que usa o menor número possível de consultórios.

Cheguei a essa decisão por dois motivos. Primeiro, o Bin Packing é NP-difícil — a solução exata exigiria explorar exponencialmente mais possibilidades, o que seria desproporcional para o tamanho do problema. Segundo, o FFD na prática produz resultados próximos do ótimo para listas como essa, e todas as regras de horário são garantidamente respeitadas.

---

### 6. Entrada para a qual o algoritmo não encontra a solução ótima

Considere esta lista:

```
Atendimento A  180min
Atendimento B  180min
Atendimento C  30min
Atendimento D  30min
```

O FFD ordena: A (180), B (180), C (30), D (30).

- A vai para a manhã do C1 → sobram 30min
- B não cabe na manhã do C1 (180+180 > 210), vai para a tarde do C1 → sobram 89min
- C não cabe na manhã do C1 (210+30 > 210), vai para a tarde do C1 (180+30 = 210) ✓
- D não cabe na manhã do C1, tenta tarde do C1 (210+30 > 269), abre C2 → vai para manhã do C2

Resultado: 2 consultórios.

Solução ótima seria:
- C1 manhã: A (180) + C (30) = 210min exatos
- C1 tarde: B (180) + D (30) = 210min exatos

Tudo em 1 consultório. O FFD não encontra isso porque quando aloca B ele não sabe que C e D ainda virão e poderiam completar a manhã do C1.

---

### 7. Complexidade de tempo

A complexidade total é **O(n²)**.

O raciocínio:

- **Ordenação:** `sort.Slice` usa Introsort, que é O(n log n).
- **Loop de alocação:** para cada um dos n atendimentos, o programa percorre os consultórios existentes para tentar encaixar. No pior caso — quando cada atendimento abre um consultório novo — existem O(n) consultórios, e percorrer todos é O(n) por atendimento. Isso resulta em O(n²) para o loop completo.
- **Impressão:** percorre cada consultório e cada atendimento uma vez, então é O(n).

O gargalo é o loop de alocação: **O(n²)** no pior caso, dominando o O(n log n) da ordenação.

Na prática o comportamento é melhor que o pior caso, porque consultórios acumulam vários atendimentos e o número real de consultórios abertos é muito menor que n.

---

## Parte 3 — Decisões de implementação

### 8. Como o programa decide quantos consultórios abrir

O programa começa com zero consultórios e abre um novo somente quando um atendimento não cabe em nenhuma sessão já existente. Não existe um número pré-definido.

O critério é: "existe alguma sessão com espaço suficiente?" Se sim, usa. Se não, abre. Isso garante que o número de consultórios é determinado pela própria lista de entrada — entradas mais curtas ou com atendimentos menores geram menos consultórios automaticamente.

---

### 9. Como os atendimentos expressos foram tratados

No momento do parse, "expresso" é convertido para 10 minutos e o label "expresso" é guardado para exibição. A partir daí, o algoritmo trata um atendimento expresso exatamente igual a qualquer outro — ele entra no sort, compete por espaço nas sessões, e é alocado pelo mesmo mecanismo.

Essa abordagem funciona porque o problema não exige tratamento especial para expressos além da duração. Converter no parse mantém o algoritmo simples e sem casos especiais.

---

### 10. Parte mais inteligente e parte que poderia ser melhorada

**Parte mais inteligente — as duas passagens de alocação:**

```go
// 1ª passagem: todas as manhãs
for _, c := range consultorios {
    if c.Manha.Cabe(at) { ... break }
}

// 2ª passagem: todas as tardes
if !alocado {
    for _, c := range consultorios {
        if c.Tarde.Cabe(at) { ... break }
    }
}
```

Tratar manhãs e tardes como passagens separadas — em vez de tentar `manhã → tarde` do mesmo consultório antes de avançar — aproveita melhor a capacidade total. Manhãs têm menos espaço (210 vs 269 minutos), então preenchê-las com prioridade deixa as tardes livres para atendimentos que não couberem em nenhuma manhã. A mudança é pequena no código mas melhora a alocação na prática.

**Parte que poderia ser melhorada — a função `imprimir`:**

```go
func imprimir(consultorios []*Consultorio) {
    fmt.Printf(...)  // escreve direto no stdout
}
```

A função escreve direto no `fmt.Printf`, o que a torna impossível de testar sem redirecionar o stdout do processo. O correto seria receber um `io.Writer` como parâmetro:

```go
func imprimir(w io.Writer, consultorios []*Consultorio) {
    fmt.Fprintf(w, ...)
}
```

Assim, no `main` passa-se `os.Stdout`, e nos testes passa-se um `bytes.Buffer` para verificar o conteúdo da saída. Da forma atual, toda a lógica de formatação de horários, higienização condicional e reunião de encerramento fica sem cobertura de testes.