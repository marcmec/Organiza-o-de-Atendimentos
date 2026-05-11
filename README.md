# Organização de Atendimentos — Clínica Veterinária Comunitária

## Descrição

Programa que distribui automaticamente atendimentos veterinários entre consultórios, respeitando as regras de horário da clínica (sessões manhã/tarde, higienização e reunião de encerramento).

## Requisitos

- Python 3.8+

## Como executar

```bash
# Com o arquivo padrão (atendimentos.txt)
python atendimentos.py

# Com outro arquivo de entrada
python atendimentos.py minha_lista.txt
```

## Como rodar os testes

```bash
python -m unittest test_atendimentos -v
```

## Estrutura do projeto

| Arquivo | Descrição |
|---|---|
| `atendimentos.py` | Código principal |
| `atendimentos.txt` | Dados de teste |
| `test_atendimentos.py` | Suíte de testes automatizados (16 testes) |
| `RACIOCINIO.md` | Justificativa do raciocínio (12 perguntas) |
| `README.md` | Este arquivo |

## Regras implementadas

- Manhã: 08:00 – 11:30 (210 min)
- Higienização: 11:30 – 13:30
- Tarde: 13:30 – até 17:59 (máx. 269 min de atendimentos)
- Reunião de encerramento: entre 17:00 e 18:00
- Atendimentos "expresso": 10 minutos
- Número de consultórios calculado automaticamente
- Algoritmo: First Fit Decreasing (bin packing)

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
