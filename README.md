# Agendador de Atendimentos Clínicos

Distribui atendimentos em consultórios de capacidade fixa, minimizando o número de
consultórios abertos. Implementa uma variante de **First-Fit Decreasing (FFD)** com
prioridade para atendimentos expressos.

## Execução

```bash
python agendador.py atendimentos.txt
python agendador.py atendimentos2.txt   # segunda entrada para robustez
```

## Testes

```bash
pip install pytest
pytest test_agendador.py -v
```

## Formato de entrada (`atendimentos.txt`)

```
<n>
<id>,<nome do paciente>,<duração em minutos>,<tipo>
```

- `tipo`: `normal` ou `expresso`
- `duração`: inteiro positivo, máximo 480 (SESSION_DURATION)

### Exemplo

```
3
1,Ana Silva,60,normal
2,Bob Souza,10,expresso
3,Carlos Lima,90,normal
```

## Arquivos do projeto

| Arquivo              | Descrição                                      |
|----------------------|------------------------------------------------|
| `agendador.py`       | Código-fonte principal                         |
| `atendimentos.txt`   | Entrada principal (15 atendimentos)            |
| `atendimentos2.txt`  | Segunda entrada para teste de robustez         |
| `test_agendador.py`  | Suite de testes (35 casos)                     |
| `RACIOCINIO.md`      | Explicação das decisões de modelagem e projeto |
