const { parseLinha } = require("../parser")
const {
    organizarAtendimentos,
    MANHA_FIM,
    REUNIAO_MINIMA,
    REUNIAO_MAXIMA
} = require("../organizador")

// Testa se o parser entende um atendimento normal com duração em minutos
test("deve transformar atendimento normal em objeto com duração", () => {
    const resultado = parseLinha("Castração de gato adulto 90min")

    expect(resultado).toEqual({
        nome: "Castração de gato adulto",
        duracao: 90,
        tipo: "NORMAL"
    })
})

// Testa se o parser transforma "expresso" em duração de 10 minutos
test("deve transformar atendimento expresso em duração de 10 minutos", () => {
    const resultado = parseLinha("Aplicação de vacina antirrábica expresso")

    expect(resultado).toEqual({
        nome: "Aplicação de vacina antirrábica",
        duracao: 10,
        tipo: "EXPRESSO"
    })
})

// Garante que nenhum atendimento da manhã passe de 11:30
test("não deve ultrapassar o horário final da manhã", () => {
    const atendimentos = [
        { nome: "Cirurgia A", duracao: 120, tipo: "NORMAL" },
        { nome: "Cirurgia B", duracao: 90, tipo: "NORMAL" },
        { nome: "Consulta C", duracao: 60, tipo: "NORMAL" }
    ]

    const resultado = organizarAtendimentos(atendimentos)

    resultado.forEach(consultorio => {
        consultorio.manha.forEach(atendimento => {
            expect(atendimento.fim).toBeLessThanOrEqual(MANHA_FIM)
        })
    })
})

// Garante que a reunião fique depois das 17h e antes das 18h
test("deve marcar reunião depois das 17h e antes das 18h", () => {
    const atendimentos = [
        { nome: "Consulta A", duracao: 60, tipo: "NORMAL" },
        { nome: "Consulta B", duracao: 60, tipo: "NORMAL" },
        { nome: "Consulta C", duracao: 60, tipo: "NORMAL" }
    ]

    const resultado = organizarAtendimentos(atendimentos)

    resultado.forEach(consultorio => {
        expect(consultorio.reuniao).toBeGreaterThanOrEqual(REUNIAO_MINIMA)
        expect(consultorio.reuniao).toBeLessThan(REUNIAO_MAXIMA)
    })
})

// Verifica se o programa abre outro consultório quando o atual fica sem espaço
test("deve abrir novo consultório quando não houver espaço", () => {
    const atendimentos = [
        { nome: "Procedimento A", duracao: 120, tipo: "NORMAL" },
        { nome: "Procedimento B", duracao: 120, tipo: "NORMAL" },
        { nome: "Procedimento C", duracao: 120, tipo: "NORMAL" },
        { nome: "Procedimento D", duracao: 120, tipo: "NORMAL" }
    ]

    const resultado = organizarAtendimentos(atendimentos)

    expect(resultado.length).toBeGreaterThan(1)
})

// Confere se todos os atendimentos foram colocados em algum consultório
test("deve organizar todos os atendimentos sem perder nenhum", () => {
    const atendimentos = [
        { nome: "A", duracao: 90, tipo: "NORMAL" },
        { nome: "B", duracao: 45, tipo: "NORMAL" },
        { nome: "C", duracao: 10, tipo: "EXPRESSO" },
        { nome: "D", duracao: 60, tipo: "NORMAL" }
    ]

    const resultado = organizarAtendimentos(atendimentos)

    // Soma quantos atendimentos foram colocados na manhã e na tarde
    const totalOrganizado = resultado.reduce((total, consultorio) => {
        return total + consultorio.manha.length + consultorio.tarde.length
    }, 0)

    expect(totalOrganizado).toBe(atendimentos.length)
})