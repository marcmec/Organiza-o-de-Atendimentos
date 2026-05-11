# Respostas das perguntas
## Parte 1 — Modelagem do problema

### 1. Como você classificou esse problema? (Ex.: empacotamento, escalonamento, busca, otimização combinatória, etc.) Justifique a escolha citando características do enunciado que apoiam essa classificação.
R: O problema em questão trata-se do problema do empacotamento, tratando da organização de dados de tamanhos variados em um menor número possível de espaços fixos. No caso do cenário, uma clínica tenta organizar atendimentos de horários variados em um espaço fixo de turno (manhã e tarde) em seus consultórios necessários.

### 2. Esse problema tem alguma semelhança com problemas clássicos da computação? Cite pelo menos um e explique a analogia em suas próprias palavras.
R: Percebi semelhanças com o Problema da Mochila, onde precisamos preencher um espaço  fixo (a mochila) com a melhor escolha de itens com tamanhos/pesos distintos.

### 3. Quais foram as estruturas de dados que você escolheu para representar consultórios, sessões e atendimentos? Por que cada uma delas? O que mudaria se você tivesse usado outra?
R: Utilizei classes para definir os Atendimentos e Consultorios, listas para armazenar a fila de atendimentos e consultórios criados, além de dados Inteiros (INT), que responde ao tempo em minutos, para simplificar a lógica de horário e espaço de tempo. 
    Parte da lógica poderia ser mantida com outra estrutura de dados, mas funções como a apresentação da organização
poderiam sofrer alterações.

## Parte 2 — Estratégia algorítmica

### 4. Descreva, em linguagem natural (sem código), o algoritmo que você implementou — passo a passo, como se estivesse explicando para um colega que nunca viu o problema.
R: 
1. O programa lê a lista de atendimentos e converte cada entrada em um objeto, identificando a duração numérica ou o termo "expresso" como 10 minutos.
2. A lista é ordenada de forma decrescente pela duração.
3. O algoritmo percorre a lista e, para cada atendimento, tenta encaixá-lo no primeiro consultório disponível que tenha espaço na sessão da manhã (até 210 min).
4. Se não couber na manhã de nenhum consultório aberto, tenta encaixar na sessão da tarde (respeitando o limite para a reunião).
5. Se um atendimento não couber em nenhum consultório existente, um novo consultório é aberto.
6. Ao final, o cronograma é gerado calculando o horário de início de cada tarefa somando as durações a partir do horário inicial de cada turno (08:00 ou 13:30).
### 5. Sua solução é **gulosa**, **exata**, **heurística** ou usa alguma outra abordagem? Como você chegou a essa decisão?
R: Heurística, pois o problema em questão depende de otimização do tempo de cada procedimento para o menor número de consultórios necessários.
### 6. Existe alguma entrada para a qual seu algoritmo **não encontraria a melhor solução possível**? Dê um exemplo concreto (pode inventar uma lista pequena de atendimentos) e explique o que aconteceria.
R: Caso houvesse um espaço de 60min restantes e sessões de [40min, 30min, 30min] o algoritmo usuaria inicialmente o de 40min, sendo que, colocar os dois de 30min seria mais eficiente.
### 7. Qual é a **complexidade de tempo** aproximada da sua solução em função do número `n` de atendimentos? Mostre seu raciocínio para chegar nessa estimativa.
R: A complexidade é O(n^2).
    A ordenação inicial leva O (n log n) para ser feita;
    A leitura de cada linha do arquivo dura um tempo igual a n (n elementos), ainda precisando verificar a lista m de consultórios abertos. Se cada atendimento precissasse de um novo consultório, levaria n x n = n^2.

## Parte 3 — Decisões de implementação

### 8. Como seu programa decide **quantos consultórios** abrir? Explique o critério.
R: O critério é a ocupação do tempo. Ele apenas cria um novo consultório caso o anterior esteja “cheio” e ainda haja atendimentos a serem realizados.
### 9. Como você tratou os atendimentos **expressos**? Por que essa abordagem?
R: Todos foram considerados como tempo igual a 10min, segundo o que o cenário informava. Essa abordagem foi adotada afim de por todos os atendimentos sob a mesma métrica, minutos.
### 10. Aponte um trecho do seu código que você considera **a parte mais inteligente** da solução, e outro que você acha que **poderia ser melhorado**. Justifique ambos.
R: Considero a parte mais inteligente o uso do Regex para encontrar o tempo dos atendimentos no texto, isso garante que mesmo que o tempo seja indicado em outro local, que não o final, ele ainda consegue localizá-lo através do indicativo "min".
    Quanto a parte que poderia receber melhorias, certamente seria o gerenciamento de tempo no turno da tarde, atualmente ele apenas garante que a reunião de encerramento começe antes das 18:00. Uma solução mais inteligente poderia garantir que ela começasse antes das 18:00 e o mais perto posssível das 17:00.