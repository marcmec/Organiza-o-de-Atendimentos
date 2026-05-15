# Raciocínio — Organizador de Atendimentos Veterinários

## Parte 1 — Modelagem do problema

### 1. Classificação do problema

Este problema é uma variante de **empacotamento em cestos** (*bin packing*) com restrições de escalonamento. Cada consultório é um "bin" composto por dois compartimentos (manhã e tarde), cada um com limites de capacidade distintos. O que o diferencia do bin packing clássico é a presença de uma **restrição de mínimo na tarde**: a sessão da tarde precisa ter entre 211 e 269 minutos de atendimentos — não basta "caber", é preciso também "preencher o suficiente".

Características do enunciado que sustentam essa classificação:
- Capacidade máxima por sessão (210 min na manhã, 269 na tarde)
- Capacidade mínima obrigatória na tarde (211 min)
- Objetivo de encaixar todos os atendimentos respeitando essas faixas
- Número de consultórios calculado dinamicamente, não fixo

### 2. Semelhança com problemas clássicos

O problema mais próximo é o **Bin Packing Problem**, classificado como NP-difícil. No bin packing clássico, dados itens de tamanhos variados e bins de capacidade fixa, o objetivo é minimizar o número de bins usados. A analogia direta é: atendimentos são os itens, sessões (manhã e tarde) são os compartimentos dos bins (consultórios).

A diferença principal é que aqui cada consultório tem dois compartimentos com regras assimétricas, e um deles possui mínimo obrigatório — algo que não existe no bin packing padrão. Também há semelhança com **Job Scheduling em máquinas paralelas**, onde tarefas (atendimentos) precisam ser alocadas em janelas de tempo em máquinas (consultórios) sem sobreposição.

### 3. Estruturas de dados

**`Appointment` (dataclass):** armazena nome, duração em minutos e o rótulo original (`expresso` ou `NNmin`). Escolhi dataclass por ser simples, imutável na prática e legível. Uma namedtuple serviria, mas dataclass permite propriedades e é mais fácil de estender.

**`Room` (dataclass com duas listas):** mantém a lista ordenada de atendimentos da manhã e da tarde separadamente. As listas preservam a ordem de inserção, que corresponde à ordem cronológica da sessão. Propriedades calculadas (`morning_used`, `afternoon_used`) derivam os totais sob demanda, evitando estado duplicado. Se tivesse usado um dicionário, perderia a tipagem e a clareza semântica; se tivesse usado uma única lista com marcação de turno, a lógica de validação ficaria mais complexa.

---

## Parte 2 — Estratégia algorítmica

### 4. Algoritmo em linguagem natural

1. **Leitura e parsing:** Cada linha do arquivo é lida e o último token identifica a duração (`expresso` → 10 min, `NNmin` → N min). O restante da linha é o nome do atendimento.

2. **Ordenação:** Os atendimentos são ordenados do maior para o menor em duração. Isso segue a estratégia FFD (*First-Fit Decreasing*): colocar os itens maiores primeiro tende a deixar menos espaço desperdiçado, porque os menores se encaixam nos buracos que sobram.

3. **Cálculo do número mínimo de consultórios:** Soma-se a duração total de todos os atendimentos e divide-se pela capacidade máxima por consultório (210 + 269 = 479 min). O resultado, arredondado para cima, é o ponto de partida.

4. **Atribuição — tarde com prioridade (best-fit decreasing):** Para cada atendimento (do maior para o menor), tenta-se alocá-lo na tarde do consultório que já está mais preenchido e ainda comporta o atendimento sem ultrapassar 269 min. Isso força o preenchimento progressivo de um consultório antes de "abrir espaço" em outro, maximizando a chance de cada tarde atingir os 211 min mínimos.

5. **Fallback para a manhã:** Se nenhuma tarde comporta o atendimento, tenta-se a manhã do consultório com menor uso que ainda caiba dentro de 210 min.

6. **Abertura de novo consultório:** Se nenhum consultório existente acomoda o atendimento, abre-se um novo e o atendimento vai para a tarde dele.

7. **Reparo pós-atribuição:** Verifica-se se alguma tarde ficou abaixo de 211 min. Se sim, move-se o menor atendimento da manhã desse mesmo consultório que resolva o déficit sem ultrapassar 269 min na tarde.

8. **Formatação da saída:** Para cada consultório, percorre-se a lista da manhã acumulando o horário a partir das 08:00, imprime-se a higienização às 11:30, depois percorre-se a lista da tarde a partir das 13:30, e imprime-se a reunião de encerramento no horário resultante.

### 5. Abordagem: gulosa heurística (FFD adaptado)

A solução é **gulosa** e **heurística**. Não garante o ótimo global (mínimo absoluto de consultórios ou distribuição ideal), mas é eficiente e suficiente para o tamanho do problema.

Cheguei a essa decisão por dois motivos:
- O problema é NP-difícil em sua forma geral, então soluções exatas (branch-and-bound, programação inteira) são desnecessariamente pesadas para n = 23.
- A heurística FFD com prioridade de tarde produz resultados válidos para a entrada dada, e o passo de reparo corrige os casos residuais onde a tarde fica abaixo do mínimo.

### 6. Caso em que o algoritmo não encontraria a melhor solução

Suponha a seguinte lista pequena:

```
Procedimento A 105min
Procedimento B 105min
Procedimento C 105min
```

Total: 315 min. Capacidade máxima por consultório: 479 min.
Mínimo de consultórios: ceil(315 / 479) = 1.

Com 1 consultório:
- A (105) → tarde: [A], usado=105
- B (105) → tarde tem 105+105=210 ≤ 269, encaixa. Tarde: [A,B], usado=210
- C (105) → tarde tem 210+105=315 > 269, não encaixa. Manhã tem 0+105=105 ≤ 210, encaixa. Manhã: [C], usado=105

Resultado: 1 consultório, manhã=105 min, tarde=210 min.
Mas tarde = 210 < 211 → violação do mínimo!

O reparo tenta mover C (105 min) da manhã para a tarde: tarde ficaria com 315 > 269 → não cabe.
Resultado: o algoritmo falharia e precisaria abrir um segundo consultório, mesmo que matematicamente 1 consultório comportasse todos os atendimentos em termos de capacidade total.

Esse é um limite inerente à heurística: ela não explora combinações alternativas de distribuição entre manhã e tarde para satisfazer o mínimo com 1 consultório.

### 7. Complexidade de tempo

- **Parsing:** O(n), uma passagem linear pelo arquivo.
- **Ordenação:** O(n log n).
- **Atribuição:** Para cada um dos n atendimentos, percorre-se a lista de consultórios (no máximo N consultórios). N ≤ n no pior caso (cada atendimento em um consultório separado). Portanto: O(n × N) = O(n²) no pior caso.
- **Reparo:** O(N × M), onde M é o número de atendimentos por manhã — limitado por n no total: O(n).
- **Formatação:** O(n).

**Complexidade total: O(n²)** no pior caso. Para n = 23, isso é negligenciável. Na prática, N é muito menor que n (3 consultórios para 23 atendimentos), então o comportamento real é próximo de O(n log n).

---

## Parte 3 — Decisões de implementação

### 8. Como o programa decide o número de consultórios

O programa soma a duração total de todos os atendimentos (T) e calcula:

```
N = ceil(T / (MORNING_MAX + AFTERNOON_MAX))
  = ceil(T / 479)
```

Para a entrada fornecida: T = 1.095 min → N = ceil(1095 / 479) = ceil(2,28) = **3 consultórios**.

Esse cálculo dá o mínimo teórico: o menor N tal que a capacidade total dos consultórios (N × 479) seja suficiente para acomodar todos os atendimentos. Se após a atribuição alguma restrição de tarde não puder ser satisfeita (o passo de reparo falhar), o programa lançaria um erro — sinalizando que N precisaria ser incrementado e o processo repetido.

### 9. Como os atendimentos expressos foram tratados

Na leitura do arquivo, o último token de cada linha é verificado: se for a string `'expresso'`, a duração é definida como 10 minutos e o rótulo original `'expresso'` é preservado; caso contrário, extrai-se o número do sufixo `NNmin`. A partir daí, atendimentos expressos são tratados exatamente como qualquer outro — apenas com duração 10. O rótulo original é guardado para reproduzir fielmente a saída.

Essa abordagem foi escolhida por ser a mais simples: o tipo do atendimento não afeta a lógica de alocação, apenas a duração importa. Preservar o rótulo evita ter que reconstruir a etiqueta na saída.

### 10. Parte mais inteligente e parte a melhorar

**Parte mais inteligente — prioridade de tarde com best-fit decreasing:**

```python
candidates = [r for r in rooms if r.afternoon_used + appt.duration <= AFTERNOON_MAX]
if candidates:
    max(candidates, key=lambda r: r.afternoon_used).afternoon.append(appt)
```

Ao escolher sempre o consultório com a tarde **mais preenchida** que ainda aceita o atendimento, o algoritmo empurra cada tarde progressivamente para além dos 211 minutos antes de distribuir para outros consultórios. Isso reduz (e na prática elimina) a necessidade do passo de reparo, porque a restrição de mínimo emerge naturalmente da estratégia de preenchimento.

**Parte a melhorar — cálculo do número de consultórios:**

O número de consultórios é calculado uma única vez com base na capacidade máxima teórica. Se o passo de reparo falhar (porque nenhuma combinação de movimentos satisfaz o mínimo de tarde com N consultórios), o programa lança uma exceção em vez de tentar automaticamente N + 1. A melhoria seria envolver todo o processo em um loop que incrementa N e tenta novamente — tornando o programa robusto para entradas adversariais onde o mínimo teórico de consultórios é inviável na prática.
