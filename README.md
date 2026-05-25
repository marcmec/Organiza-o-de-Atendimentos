# Organizador de Atendimentos — Clínica Veterinária Comunitária

Programa que distribui automaticamente atendimentos veterinários entre consultórios, respeitando as regras de funcionamento da clínica.

## Pré-requisitos

- Python 3.8 ou superior (sem dependências externas para o programa principal)
- `pytest` para rodar os testes: `pip install pytest`

## Estrutura do repositório

```
.
├── organizador.py     # Programa principal
├── testes.py          # Suíte de testes automatizados
├── atendimentos.txt   # Arquivo de entrada com os atendimentos
├── RACIOCINIO.md      # Justificativa do raciocínio (12 perguntas)
└── README.md          # Este arquivo
```

## Como executar

### Rodando com o arquivo padrão

```bash
python3 organizador.py atendimentos.txt
```

### Rodando com outro arquivo de entrada

```bash
python3 organizador.py minha_entrada.txt
```

### Formato do arquivo de entrada

Cada linha deve seguir um dos dois formatos:

```
Nome do atendimento 90min
Nome do atendimento expresso
```

- Nomes não contêm números.
- `expresso` equivale a 10 minutos.
- Linhas em branco e linhas começando com `#` são ignoradas.

### Exemplo de saída

```
Consultorio 1:
  11:30 Higienizacao
  13:30 Cirurgia ortopedica em cao atropelado 120min
  15:30 Avaliacao dermatologica em cao com sarna 45min
  16:15 Exame de sangue completo 30min
  16:45 Raio-X de pata traseira 30min
  17:15 Reuniao de encerramento

Consultorio 2:
  ...
```

## Como rodar os testes

```bash
python3 -m pytest testes.py -v
```

Saída esperada: **39 passed**.

Para rodar apenas uma categoria de testes:

```bash
python3 -m pytest testes.py::TestParser -v
python3 -m pytest testes.py::TestRegras -v
python3 -m pytest testes.py::TestFormatacao -v
```

## Regras respeitadas pelo programa

| Regra | Implementação |
|---|---|
| Manhã começa às 08:00 e termina às 11:30 | Sessão com capacidade de 210 min |
| Tarde começa às 13:30 | `TARDE_INICIO = 13 * 60 + 30` |
| Reunião após 17:00 | Tarde deve ter ≥ 210 min de atendimentos |
| Reunião antes das 18:00 | Tarde deve ter ≤ 269 min de atendimentos |
| Atendimento expresso = 10 min | `DURACAO_EXPRESSO = 10` |
| Número de consultórios calculado dinamicamente | `ceil(total / 269)` como ponto de partida |

## Algoritmo em resumo

1. Calcula o número mínimo de consultórios: `ceil(total_minutos / 269)`
2. Ordena os atendimentos do maior para o menor (LPT)
3. Aloca cada atendimento na tarde com menor carga que ainda o aceita (LPT balanceado)
4. O que não couber nas tardes vai para as manhãs (máximo 210 min cada)
5. Valida todas as regras e exibe a agenda formatada

Mais detalhes em [RACIOCINIO.md](RACIOCINIO.md).
