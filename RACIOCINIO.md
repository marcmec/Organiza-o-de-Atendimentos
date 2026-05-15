# RACIOCÍNIO - Organização de Atendimentos

## Parte 1 — Modelagem do problema

### 1. Classificação do problema

Classifiquei o problema como **escalonamento com restrição de tempo** e também com uma ideia de **empacotamento**.

É escalonamento porque o programa precisa montar uma agenda, definindo onde cada atendimento entra. É parecido com empacotamento porque cada consultório tem uma capacidade limitada de tempo: manhã das 08:00 às 11:30 e tarde a partir das 13:30.

O objetivo é encaixar todos os atendimentos nesses blocos, abrindo novos consultórios apenas quando necessário.

---

### 2. Semelhança com problema clássico

O problema lembra o **Bin Packing Problem**.

No Bin Packing, temos itens de tamanhos diferentes e precisamos colocá-los em caixas com capacidade limitada.

Neste desafio:

- os atendimentos são os itens;
- a duração é o tamanho;
- os consultórios são as caixas;
- manhã e tarde são os espaços disponíveis.

Também tem relação com escalonamento, porque o programa monta os horários dos atendimentos.

---

### 3. Estruturas de dados escolhidas

Usei objetos para representar os atendimentos:

{
    nome: "Castração de gato adulto",
    duracao: 90,
    tipo: "NORMAL"
}

Usei objeto porque deixa o código mais claro do que usar posições em array.

Para os consultórios, usei um objeto com duas listas:

{
    manha: [],
    tarde: [],
    proximoHorarioManha: 480,
    proximoHorarioTarde: 810
}

A manhã e a tarde são arrays porque guardam uma sequência de atendimentos.

Os horários foram guardados em minutos, porque isso facilita os cálculos. Por exemplo, 08:00 vira 480 e 11:30 vira 690. Assim, para calcular o fim de um atendimento, basta fazer:

fim = inicio + atendimento.duracao

## Parte 2 — Estratégia algorítmica
### 4. Descrição do algoritmo

O programa lê o arquivo atendimentos.txt e transforma cada linha em um atendimento.

Se a linha termina com expresso, o atendimento recebe duração de 10 minutos. Se termina com algo como 90min, o programa extrai esse número como duração.

Depois, os atendimentos são ordenados do maior para o menor. Fiz isso porque atendimentos longos são mais difíceis de encaixar se ficarem para o final.

Para cada atendimento, o programa tenta:

encaixar na manhã de um consultório existente;
se não couber, tenta encaixar na tarde;
se não couber em nenhum consultório, abre um novo.

No final, imprime os atendimentos da manhã, a higienização às 11:30, os atendimentos da tarde e a reunião de encerramento.

## 5. Tipo de abordagem

Minha solução é gulosa com heurística.

Ela é gulosa porque, quando encontra um consultório onde o atendimento cabe, coloca ali e não tenta reorganizar depois.

A heurística usada foi ordenar por duração decrescente, parecida com First Fit Decreasing. Escolhi isso porque é simples, fácil de explicar e funciona bem para um desafio júnior.

## 6. Caso em que não encontra a melhor solução

Sim, pode acontecer.

Exemplo:

Atendimento A 110min
Atendimento B 100min
Atendimento C 100min
Atendimento D 60min
Atendimento E 50min
Atendimento F 50min

Como o algoritmo sempre aceita o primeiro encaixe possível, ele pode deixar espaços sobrando que não combinam bem com os próximos atendimentos.

Uma solução perfeita teria que testar várias combinações, mas meu programa não faz isso. Ele prioriza simplicidade e legibilidade.

## 7. Complexidade de tempo

A ordenação dos atendimentos custa:

O(n log n)

Depois, para cada atendimento, o programa pode verificar vários consultórios. No pior caso, isso chega a:

O(n²)

Então a complexidade aproximada final é:

O(n²)
Parte 3 — Decisões de implementação
## 8. Como decide quantos consultórios abrir?

O programa começa sem consultórios.

Para cada atendimento, ele tenta usar os consultórios já existentes. Se o atendimento não couber em nenhum deles, cria um novo consultório.

Então o número de consultórios não é fixo. Ele surge conforme a necessidade.

## 9. Como tratei os expressos?

Atendimentos expressos foram tratados como atendimentos de 10 minutos.

Exemplo:

Aplicação de vacina antirrábica expresso

vira:

{
    nome: "Aplicação de vacina antirrábica",
    duracao: 10,
    tipo: "EXPRESSO"
}

Mantive o campo tipo porque ele pode ser útil se depois eu quiser destacar ou filtrar os expressos.

## 10. Parte mais inteligente da solução

A parte mais importante é a lógica de encaixe.

O programa pega o próximo horário livre da sessão, soma a duração do atendimento e verifica se ultrapassa o limite.

Na manhã, não pode passar de 11:30.
Na tarde, não pode impedir a reunião antes das 18:00.

Essa escolha deixou as regras do enunciado simples de implementar.

## 11. Parte que poderia melhorar

A estratégia de distribuição poderia ser melhor.

Hoje o programa usa uma solução gulosa. Ela é simples, mas não garante a menor quantidade possível de consultórios.

Uma melhoria seria testar combinações diferentes com backtracking ou usar uma estratégia que escolha o consultório com melhor aproveitamento de tempo