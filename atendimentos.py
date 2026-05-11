import datetime
import sys


class Atendimento:
    def __init__(self, linha):
        linha = linha.strip()
        if linha.endswith("expresso"):
            self.nome = linha
            self.duracao = 10
        else:
            partes = linha.rsplit(' ', 1)
            self.nome = partes[0]
            self.duracao = int(partes[1].replace('min', ''))

    def __repr__(self):
        if self.duracao == 10 and self.nome.endswith("expresso"):
            return self.nome
        return f"{self.nome} {self.duracao}min"


# Capacidades em minutos
MANHA_MAX = 210   # 08:00 - 11:30
TARDE_MIN = 210   # 13:30 - 17:00 (reunião não pode ser antes das 17:00)
TARDE_MAX = 269   # 13:30 - 17:59 (reunião deve começar antes das 18:00)


class Consultorio:
    def __init__(self, id):
        self.id = id
        self.manha = []
        self.tarde = []
        self.usado_manha = 0
        self.usado_tarde = 0

    def cabe_manha(self, duracao):
        return self.usado_manha + duracao <= MANHA_MAX

    def cabe_tarde(self, duracao):
        # Atendimentos não podem ultrapassar as 18:00
        # e a reunião deve começar >= 17:00 (ou seja, usado_tarde <= TARDE_MAX)
        return self.usado_tarde + duracao <= TARDE_MAX

    def adicionar_manha(self, att):
        self.manha.append(att)
        self.usado_manha += att.duracao

    def adicionar_tarde(self, att):
        self.tarde.append(att)
        self.usado_tarde += att.duracao

    def adicionar(self, att):
        """Tenta alocar na manhã, depois na tarde. Retorna True se conseguiu."""
        if self.cabe_manha(att.duracao):
            self.adicionar_manha(att)
            return True
        elif self.cabe_tarde(att.duracao):
            self.adicionar_tarde(att)
            return True
        return False

    def horario_reuniao(self):
        """Retorna o horário da reunião de encerramento (datetime)."""
        inicio_tarde = datetime.datetime(2000, 1, 1, 13, 30)
        fim_atendimentos = inicio_tarde + datetime.timedelta(minutes=self.usado_tarde)
        minimo = datetime.datetime(2000, 1, 1, 17, 0)
        return max(fim_atendimentos, minimo)

    def imprimir(self):
        print(f"Consultório {self.id}:")

        curr = datetime.datetime(2000, 1, 1, 8, 0)
        for a in self.manha:
            print(f"{curr.strftime('%H:%M')} {a}")
            curr += datetime.timedelta(minutes=a.duracao)
        print("11:30 Higienização")

        curr = datetime.datetime(2000, 1, 1, 13, 30)
        for a in self.tarde:
            print(f"{curr.strftime('%H:%M')} {a}")
            curr += datetime.timedelta(minutes=a.duracao)

        reuniao = self.horario_reuniao()
        print(f"{reuniao.strftime('%H:%M')} Reunião de encerramento")
        print()


def organizar_clinica(atendimentos_lista):
    """Organiza atendimentos nos consultórios usando First Fit Decreasing."""
    atendimentos = [Atendimento(ln) for ln in atendimentos_lista if ln.strip()]
    # First Fit Decreasing: ordena por duração decrescente para melhor empacotamento
    atendimentos.sort(key=lambda x: x.duracao, reverse=True)

    consultorios = []

    for att in atendimentos:
        alocado = False
        for c in consultorios:
            if c.adicionar(att):
                alocado = True
                break

        if not alocado:
            novo_c = Consultorio(len(consultorios) + 1)
            novo_c.adicionar(att)
            consultorios.append(novo_c)

    return consultorios


def carregar_atendimentos(caminho):
    """Carrega atendimentos de um arquivo texto."""
    with open(caminho, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]


if __name__ == '__main__':
    caminho = sys.argv[1] if len(sys.argv) > 1 else 'atendimentos'
    dados = carregar_atendimentos(caminho)
    resultado = organizar_clinica(dados)
    for c in resultado:
        c.imprimir()