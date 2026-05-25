# Organizador de Atendimentos

Programa em Python que organiza automaticamente atendimentos de uma clínica em consultórios, separando horários de manhã e tarde.

## Objetivo

Distribuir atendimentos entre consultórios respeitando:

- início da manhã às 08:00;
- fim da manhã às 11:30;
- início da tarde às 13:30;
- reunião de encerramento antes das 18:00;
- atendimento expresso com duração de 10 minutos;
- higienização ao final da manhã.

## Estrutura

```text
.
├── organizador.py
├── atendimentos.txt
├── raciocinio.md
├── saida_exemplo.txt
└── README.md
```

## Como executar

```bash
python organizador.py atendimentos.txt
```

Ou, se estiver no Linux/Mac:

```bash
python3 organizador.py atendimentos.txt
```

## Formato do arquivo de entrada

Cada linha deve seguir um destes modelos:

```text
Nome do atendimento 60min
Nome do atendimento expresso
```

Exemplo:

```text
Consulta de rotina em cachorro 30min
Aplicação de vacina antirrábica expresso
Castração de gato adulto 90min
```

Linhas vazias e linhas iniciadas com `#` são ignoradas.

## Estratégia usada

O programa ordena os atendimentos do maior para o menor e tenta colocá-los primeiro nos períodos da tarde, escolhendo sempre o consultório com menor carga de trabalho. Depois, os atendimentos que não couberem são colocados nos períodos da manhã.

Essa estratégia ajuda a equilibrar os consultórios e evita que um consultório fique muito cheio enquanto outro fica quase vazio.

## Explicação da lógica

A explicação completa do raciocínio usado no algoritmo está no arquivo `raciocinio.md`.
