# Raciocínio do Projeto

Este arquivo explica a lógica usada no programa `organizador.py`.

## 1. Problema resolvido

O objetivo do programa é organizar uma lista de atendimentos em consultórios diferentes, respeitando os horários disponíveis durante o dia.

Cada atendimento possui:

- nome;
- duração em minutos;
- ou a palavra `expresso`, que representa 10 minutos.

O programa lê esses dados de um arquivo `.txt` e monta uma agenda final.

## 2. Regras de horário

O sistema considera dois períodos principais:

### Manhã

- começa às 08:00;
- termina às 11:30;
- depois disso ocorre a higienização.

Tempo disponível de manhã:

```text
08:00 até 11:30 = 210 minutos
```

### Tarde

- começa às 13:30;
- precisa terminar antes das 18:00;
- ao final ocorre a reunião de encerramento.

Tempo máximo da tarde:

```text
13:30 até antes de 18:00
```

No código, a tarde usa uma capacidade segura para impedir que a reunião ultrapasse o limite.

## 3. Leitura dos atendimentos

A função `ler_atendimentos()` percorre cada linha do arquivo de entrada.

Ela aceita dois formatos:

```text
Nome do atendimento 60min
Nome do atendimento expresso
```

Quando encontra `expresso`, o programa converte para 10 minutos.

Exemplo:

```text
Triagem rápida expresso
```

vira internamente:

```text
Triagem rápida = 10 minutos
```

Se a linha não estiver em um formato válido, o programa mostra erro.

## 4. Estrutura usada no código

O projeto usa três estruturas principais com `dataclass`:

### Atendimento

Representa um atendimento individual.

Guarda:

- nome;
- duração;
- se é expresso ou não.

### Periodo

Representa um turno, como manhã ou tarde.

Guarda:

- horário de início;
- capacidade total;
- lista de atendimentos alocados.

Também calcula:

- tempo usado;
- tempo livre;
- se um atendimento ainda cabe naquele período.

### Consultorio

Representa um consultório completo.

Cada consultório possui:

- um período da manhã;
- um período da tarde.

## 5. Estratégia de organização

A função principal da lógica é `organizar()`.

Ela segue estes passos:

### Passo 1: verificar se algum atendimento é grande demais

Antes de organizar, o programa verifica se existe algum atendimento que não cabe nem na manhã nem na tarde.

Se existir, ele gera erro.

### Passo 2: calcular uma quantidade inicial de consultórios

O programa soma a duração total dos atendimentos e estima uma quantidade inicial de consultórios.

A ideia é começar com uma quantidade razoável para evitar criar consultórios demais ou de menos.

### Passo 3: ordenar do maior para o menor

Os atendimentos são ordenados pela duração, do maior para o menor.

Isso é importante porque atendimentos longos são mais difíceis de encaixar.

Se deixarmos os maiores por último, pode acontecer de sobrar apenas espaços pequenos.

### Passo 4: tentar preencher primeiro a tarde

O programa tenta colocar os atendimentos primeiro nos períodos da tarde.

Isso acontece porque a tarde precisa terminar perto do horário da reunião de encerramento, mas sem passar das 18:00.

### Passo 5: colocar o que sobrar de manhã

Os atendimentos que não couberem à tarde são enviados para os períodos da manhã.

### Passo 6: criar novos consultórios se necessário

Se ainda existirem atendimentos sem lugar, o programa cria mais consultórios até conseguir encaixar todos.

## 6. Critério para escolher onde colocar um atendimento

A função `distribuir_em_periodos()` recebe uma lista de atendimentos e uma lista de períodos disponíveis.

Para cada atendimento, ela:

1. verifica em quais períodos ele cabe;
2. escolhe o período com menor tempo usado;
3. adiciona o atendimento nesse período.

Esse critério ajuda a equilibrar a carga entre os consultórios.

## 7. Validação

Depois de organizar, a função `validar()` confere se:

- nenhum atendimento ficou faltando;
- nenhum atendimento foi duplicado;
- a manhã não passou das 11:30;
- a reunião de encerramento não ficou depois do limite permitido.

Se encontrar algum problema, o programa mostra uma mensagem de erro.

## 8. Geração da agenda

A função `gerar_agenda()` monta o texto final da agenda.

Ela imprime cada consultório separadamente, mostrando:

- atendimentos da manhã;
- horário de higienização;
- atendimentos da tarde;
- horário da reunião de encerramento.

Exemplo de saída:

```text
Consultório 1:
 Manhã:
  08:00 - Consulta de rotina (30min)
  08:30 - Vacinação rápida (expresso)
  11:30 - Higienização
 Tarde:
  13:30 - Procedimento clínico (90min)
  15:00 - Retorno avaliativo (30min)
  15:30 - Reunião de encerramento
```

## 9. Por que essa solução é parecida com o projeto de referência?

Ela segue a mesma ideia geral:

- ler atendimentos de um arquivo de texto;
- interpretar durações em minutos e atendimentos expressos;
- distribuir automaticamente em locais/consultórios;
- respeitar horários fixos;
- imprimir uma agenda organizada no terminal.

Porém, o código foi escrito de forma própria, com nomes e organização diferentes, para servir como uma versão adaptável.

## 10. Possíveis melhorias

Algumas melhorias possíveis seriam:

- salvar a saída em um arquivo `.txt` automaticamente;
- permitir configurar horários pelo usuário;
- criar uma interface gráfica;
- separar o código em mais arquivos;
- gerar relatório em PDF;
- permitir diferentes tipos de atendimento com prioridades.
