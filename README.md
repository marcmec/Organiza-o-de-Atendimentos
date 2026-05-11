# Organização de Atendimentos em uma Clínica Veterinária

## Contexto

Você foi contratado(a) por uma clínica veterinária comunitária que oferece atendimento gratuito para animais de rua resgatados por ONGs da região. A clínica possui **vários consultórios** funcionando em paralelo, e cada um deles atende em **dois turnos diários**: manhã e tarde.

Os organizadores receberam uma lista enorme de pedidos de atendimento (consultas, exames, cirurgias, procedimentos) e estão tendo dificuldade em distribuí-los entre os consultórios respeitando as regras da clínica. Sua missão é escrever um programa que faça essa organização automaticamente.

## Regras de funcionamento

- A clínica possui **vários consultórios** (tracks), cada um com uma agenda independente.
- Cada consultório tem uma **sessão da manhã** e uma **sessão da tarde**.
- A **sessão da manhã** começa às **08:00** e deve terminar até as **11:30**, quando começa a higienização dos consultórios.
- A **sessão da tarde** começa às **13:30** e deve terminar a tempo da **reunião de encerramento da equipe**.
- A reunião de encerramento deve começar **depois das 17:00**, mas **antes das 18:00**.
- Nenhum dos nomes dos atendimentos contém números.
- A duração de cada atendimento é dada em **minutos** ou marcada como **expresso** (atendimentos rápidos de 10 minutos, como aplicação de vacina).
- Não há intervalos entre os atendimentos — a equipe está bem coordenada.
- O número de consultórios necessários deve ser **calculado pelo seu programa** com base na lista de entrada (ou seja, ele não é fixo).

## Dados para teste (arquivo `atendimentos.txt`)

```
Castração de gato adulto 90min
Aplicação de vacina antirrábica expresso
Limpeza dentária em cão de pequeno porte 45min
Consulta de rotina em filhote de gato 30min
Exame de sangue completo 30min
Cirurgia ortopédica em cão atropelado 120min
Avaliação dermatológica em cão com sarna 45min
Microchipagem expresso
Retirada de pontos pós-cirúrgicos 30min
Atendimento de emergência respiratória 60min
Consulta com nutricionista veterinária 45min
Ultrassonografia abdominal 60min
Castração de cadela em fase reprodutiva 90min
Vermifugação em ninhada de filhotes 30min
Avaliação cardiológica em cão idoso 60min
Curativo de ferida exposta 30min
Aplicação de vacina V10 expresso
Consulta comportamental para gato resgatado 45min
Raio-X de pata traseira 30min
Tratamento de otite em cão 30min
Cirurgia de remoção de tumor cutâneo 90min
Resgate emocional: socialização de gato feral 60min
Avaliação ortopédica em cão com displasia 45min
```

## Resultado esperado (formato de saída)

```
Consultório 1:
08:00 [atendimento] [duração]
...
11:30 Higienização
13:30 [atendimento] [duração]
...
17:XX Reunião de encerramento

Consultório 2:
...
```

A combinação exata dos atendimentos pode variar conforme a abordagem escolhida — o que importa é que **todas as regras sejam respeitadas**.

---

## ⚠️ Diferencial deste desafio: Justificativa do raciocínio

Além do código funcionando, este desafio exige que você **explique o raciocínio por trás da sua solução**. A entrega deve incluir um arquivo `RACIOCINIO.md` no repositório respondendo às perguntas abaixo. Respostas genéricas ou copiadas de tutoriais serão desconsideradas.

### Parte 1 — Modelagem do problema

1. Como você classificou esse problema? (Ex.: empacotamento, escalonamento, busca, otimização combinatória, etc.) Justifique a escolha citando características do enunciado que apoiam essa classificação.
2. Esse problema tem alguma semelhança com problemas clássicos da computação? Cite pelo menos um e explique a analogia em suas próprias palavras.
3. Quais foram as estruturas de dados que você escolheu para representar consultórios, sessões e atendimentos? Por que cada uma delas? O que mudaria se você tivesse usado outra?

### Parte 2 — Estratégia algorítmica

4. Descreva, em linguagem natural (sem código), o algoritmo que você implementou — passo a passo, como se estivesse explicando para um colega que nunca viu o problema.
5. Sua solução é **gulosa**, **exata**, **heurística** ou usa alguma outra abordagem? Como você chegou a essa decisão?
6. Existe alguma entrada para a qual seu algoritmo **não encontraria a melhor solução possível**? Dê um exemplo concreto (pode inventar uma lista pequena de atendimentos) e explique o que aconteceria.
7. Qual é a **complexidade de tempo** aproximada da sua solução em função do número `n` de atendimentos? Mostre seu raciocínio para chegar nessa estimativa.

### Parte 3 — Decisões de implementação

8. Como seu programa decide **quantos consultórios** abrir? Explique o critério.
9. Como você tratou os atendimentos **expressos**? Por que essa abordagem?
10. Aponte um trecho do seu código que você considera **a parte mais inteligente** da solução, e outro que você acha que **poderia ser melhorado**. Justifique ambos.


### Instruções de execução
Ao abrir este projeto, basta navegar até o arquivo main.py e clicar no Botão Play no canto superior direito (se for no VScode) para rodar o código. A resposta será exibida no terminal.