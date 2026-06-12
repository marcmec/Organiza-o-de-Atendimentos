"""Ponto de entrada do programa.

Uso:
    python main.py                 # lê o arquivo padrão "atendimentos.txt"
    python main.py outra_lista.txt # lê outro arquivo de entrada
"""

import sys

from clinica.parser import carregar
from clinica.escalonador import organizar
from clinica.relatorio import formatar_agenda


def main(argv: list) -> int:
    # No Windows o console às vezes usa cp1252 e embaralha acentos; forçamos
    # UTF-8 na saída para que "Consultório", "Higienização" etc. saiam certos.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass  # ambientes mais antigos: seguimos com a codificação padrão

    caminho = argv[1] if len(argv) > 1 else "atendimentos.txt"

    try:
        atendimentos = carregar(caminho)
    except FileNotFoundError:
        print(f"Arquivo de entrada não encontrado: {caminho}", file=sys.stderr)
        return 1

    if not atendimentos:
        print("Nenhum atendimento na entrada — nada a organizar.", file=sys.stderr)
        return 1

    try:
        consultorios = organizar(atendimentos)
    except ValueError as erro:
        print(str(erro), file=sys.stderr)
        return 2

    print(formatar_agenda(consultorios), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
