from models import Consultorio

def formatar_hora(total_minutos):
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas:02d}:{minutos:02d}"

def organizar_atendimentos(lista_ordenada):
    consultorios = []
    restantes = lista_ordenada[:]
    
    proximo_id = 1
    while restantes:
        c = Consultorio(proximo_id)
        
        # Encaixe Manhã
        i = 0
        while i < len(restantes):
            if c.pode_receber_manha(restantes[i].duracao):
                atend = restantes.pop(i)
                c.sessao_manha.append(atend)
                c.minutos_manha += atend.duracao
            else:
                i += 1
        
        # Encaixe Tarde
        i = 0
        while i < len(restantes):
            if c.pode_receber_tarde(restantes[i].duracao):
                atend = restantes.pop(i)
                c.sessao_tarde.append(atend)
                c.minutos_tarde += atend.duracao
            else:
                i += 1
        
        consultorios.append(c)
        proximo_id += 1
        
    return consultorios

def exibir_cronograma(consultorios):
    for c in consultorios:
        print(f"Consultório {c.id}:")
        
        # Manhã
        hora = 8 * 60
        for a in c.sessao_manha:
            dur = "expresso" if a.duracao == 10 else f"{a.duracao}min"
            print(f"{formatar_hora(hora)} {a.descricao} {dur}")
            hora += a.duracao
        print("11:30 Higienização")
        
        # Tarde
        hora = 13 * 60 + 30
        for a in c.sessao_tarde:
            dur = "expresso" if a.duracao == 10 else f"{a.duracao}min"
            print(f"{formatar_hora(hora)} {a.descricao} {dur}")
            hora += a.duracao
            
        horario_reuniao = max(hora, 17 * 60)
        print(f"{formatar_hora(horario_reuniao)} Reunião de encerramento\n")