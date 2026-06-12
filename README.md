# Organização de Atendimentos — Clínica Veterinária

Solução para o desafio de **organização de atendimentos** de uma clínica
veterinária com vários consultórios. O programa lê uma lista de atendimentos e
distribui cada um entre os consultórios (e dentro deles, entre a sessão da manhã
e a da tarde) respeitando as regras da clínica, calculando **automaticamente**
quantos consultórios são necessários.

> O raciocínio completo (modelagem, escolha do algoritmo, complexidade, limites)
> está em **[RACIOCINIO.md](RACIOCINIO.md)**.

## Regras implementadas

- Vários consultórios em paralelo, cada um com **manhã** e **tarde**.
- **Manhã:** 08:00 → 11:30 (no máx. **210 min**), depois **higienização** às 11:30.
- **Tarde:** começa às **13:30** e termina a tempo da **reunião de encerramento**.
- A reunião começa **a partir das 17:00 e antes das 18:00** → a tarde tem entre
  **210 e 270 minutos** (janela `[210, 270)`).
- Atendimento **`expresso`** = **10 minutos**.
- O número de consultórios é **calculado**, não fixado.

## Como executar

Pré-requisito: **Python 3.8+** (testado com 3.12). Não há dependências externas.

A partir da raiz do projeto:

```bash
# usa o arquivo padrão atendimentos.txt
python main.py

# ou aponte para outro arquivo de entrada
python main.py outra_lista.txt
```

A saída é impressa no terminal, um bloco por consultório.

### Salvando a saída em arquivo (Windows / PowerShell)

O operador `>` do PowerShell 5.1 grava em UTF-16 e pode embaralhar acentos. Para
um arquivo UTF-8 limpo, use:

```powershell
python main.py | Out-File -Encoding utf8 saida.txt
```

No `cmd` ou em terminais já em UTF-8, `python main.py > saida.txt` funciona.
Um exemplo de saída para a entrada oficial está em
[`saida_oficial.txt`](saida_oficial.txt).

## Como rodar os testes

```bash
python -m unittest discover -s tests -v
```

São 19 testes cobrindo: parsing (incluindo nome com número, como "V10"),
o valor do expresso, todas as regras de horário sobre a agenda gerada, o número
de consultórios para a entrada oficial, casos-limite (lista vazia, entrada
inviável, um único atendimento grande) e o critério de **robustez** (uma segunda
entrada semelhante também produz agenda válida).

## Formato da entrada (`atendimentos.txt`)

Uma linha por atendimento: `<nome> <duração>`, onde a duração é o **último
token** e vale `<n>min` (ex.: `90min`) ou `expresso`. Exemplo:

```
Castração de gato adulto 90min
Aplicação de vacina antirrábica expresso
Cirurgia ortopédica em cão atropelado 120min
```

> O parser olha apenas o último token para descobrir a duração, então nomes que
> contêm números (ex.: "vacina **V10** expresso") não confundem a leitura.

## Exemplo de saída (entrada oficial)

```
Consultório 1:
08:00 Consulta com nutricionista veterinária 45min
...
11:30 Higienização
13:30 Cirurgia ortopédica em cão atropelado 120min
...
17:30 Reunião de encerramento

Consultório 2:
...
```

A entrada oficial (1095 minutos no total) é organizada em **3 consultórios**,
todos com a manhã encerrando até as 11:30 e a reunião entre 17:30 e 17:55.

## Estrutura do projeto

```
.
├── main.py                  # ponto de entrada (CLI)
├── atendimentos.txt         # entrada oficial do desafio
├── saida_oficial.txt        # exemplo de saída para a entrada oficial
├── clinica/                 # pacote com a lógica
│   ├── regras.py            # horários e capacidades (constantes)
│   ├── modelos.py           # Atendimento, Sessao, Consultorio
│   ├── parser.py            # leitura do arquivo de entrada
│   ├── escalonador.py       # o algoritmo de organização
│   └── relatorio.py         # formatação da agenda final
├── tests/
│   └── test_clinica.py      # suíte de testes (unittest)
├── RACIOCINIO.md            # justificativa do raciocínio (12 perguntas)
└── README.md
```
