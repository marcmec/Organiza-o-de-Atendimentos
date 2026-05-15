// Horários fixos da clínica, salvos em minutos
const MANHA_INICIO = 8 * 60              // 08:00
const MANHA_FIM = 11 * 60 + 30          // 11:30

const TARDE_INICIO = 13 * 60 + 30       // 13:30

const REUNIAO_MINIMA = 17 * 60 + 1      // depois das 17:00
const REUNIAO_MAXIMA = 18 * 60          // antes das 18:00

// Cria um consultório vazio, com manhã e tarde livres
function criarConsultorio() {
    return {
        manha: [],
        tarde: [],
        proximoHorarioManha: MANHA_INICIO,
        proximoHorarioTarde: TARDE_INICIO,
        higienizacao: MANHA_FIM,
        reuniao: REUNIAO_MINIMA
    }
}

// Tenta colocar um atendimento na parte da manhã
function encaixarNaManha(consultorio, atendimento) {
    const inicio = consultorio.proximoHorarioManha
    const fim = inicio + atendimento.duracao

    // Se passar de 11:30, não cabe na manhã
    if (fim > MANHA_FIM) {
        return false
    }

    // Adiciona o atendimento já com horário de início e fim
    consultorio.manha.push({
        ...atendimento,
        inicio,
        fim
    })

    // Atualiza o próximo horário livre da manhã
    consultorio.proximoHorarioManha = fim

    return true
}

// Tenta colocar um atendimento na parte da tarde
function encaixarNaTarde(consultorio, atendimento) {
    const inicio = consultorio.proximoHorarioTarde
    const fim = inicio + atendimento.duracao

    // Se chegar em 18:00 ou passar, não pode, porque precisa ter reunião antes
    if (fim >= REUNIAO_MAXIMA) {
        return false
    }

    consultorio.tarde.push({
        ...atendimento,
        inicio,
        fim
    })

    // Atualiza o próximo horário livre da tarde
    consultorio.proximoHorarioTarde = fim

    // A reunião fica depois do último atendimento da tarde,
    // mas nunca antes de 17:01
    consultorio.reuniao = Math.max(consultorio.proximoHorarioTarde, REUNIAO_MINIMA)

    return true
}

// Tenta encaixar o atendimento primeiro na manhã, depois na tarde
function encaixarAtendimento(consultorio, atendimento) {
    if (encaixarNaManha(consultorio, atendimento)) {
        return true
    }

    if (encaixarNaTarde(consultorio, atendimento)) {
        return true
    }

    return false
}

// Remove informações internas que só eram usadas durante o cálculo
function finalizarConsultorio(consultorio) {
    return {
        manha: consultorio.manha,
        tarde: consultorio.tarde,
        higienizacao: consultorio.higienizacao,
        reuniao: Math.max(consultorio.proximoHorarioTarde, REUNIAO_MINIMA)
    }
}

// Função principal: organiza todos os atendimentos nos consultórios
function organizarAtendimentos(atendimentos) {
    const lista = atendimentos
        .filter(atendimento => atendimento !== null)
        // Ordena do maior para o menor para tentar encaixar os mais difíceis primeiro
        .sort((a, b) => b.duracao - a.duracao)

    const consultorios = []

    for (const atendimento of lista) {
        let colocado = false

        // Tenta colocar nos consultórios que já existem
        for (const consultorio of consultorios) {
            if (encaixarAtendimento(consultorio, atendimento)) {
                colocado = true
                break
            }
        }

        // Se não coube em nenhum, abre um novo consultório
        if (!colocado) {
            const novoConsultorio = criarConsultorio()

            if (!encaixarAtendimento(novoConsultorio, atendimento)) {
                throw new Error(
                    `Atendimento muito longo para caber em uma sessão: ${atendimento.nome}`
                )
            }

            consultorios.push(novoConsultorio)
        }
    }

    return consultorios.map(finalizarConsultorio)
}

module.exports = {
    organizarAtendimentos,
    MANHA_INICIO,
    MANHA_FIM,
    TARDE_INICIO,
    REUNIAO_MINIMA,
    REUNIAO_MAXIMA
}