const fs = require("fs")

const { parseLinha } = require("./parser")
const { organizarAtendimentos } = require("./organizador")

// Converte minutos para formato de hora.
// Exemplo: 480 vira "08:00"
function minutosParaHora(minutos) {
    const horas = Math.floor(minutos / 60)
    const mins = minutos % 60

    return `${String(horas).padStart(2, "0")}:${String(mins).padStart(2, "0")}`
}

// Lê o arquivo de entrada com todos os atendimentos
const texto = fs.readFileSync("atendimentos.txt", "utf-8")

// Separa o texto em linhas e remove linhas vazias
const linhas = texto
    .trim()
    .split("\n")
    .filter(linha => linha.trim() !== "")

// Transforma cada linha em um objeto de atendimento
// Exemplo: "Castração 90min" vira { nome, duracao, tipo }
const atendimentos = linhas.map(parseLinha)

// Organiza os atendimentos nos consultórios
const consultorios = organizarAtendimentos(atendimentos)

// Mostra o resultado final no terminal
consultorios.forEach((consultorio, indice) => {
    console.log(`Consultório ${indice + 1}:`)

    // Imprime os atendimentos da manhã
    consultorio.manha.forEach(atendimento => {
        console.log(
            `${minutosParaHora(atendimento.inicio)} ${atendimento.nome} ${atendimento.duracao}min`
        )
    })

    // Horário fixo de higienização
    console.log(`${minutosParaHora(consultorio.higienizacao)} Higienização`)

    // Imprime os atendimentos da tarde
    consultorio.tarde.forEach(atendimento => {
        console.log(
            `${minutosParaHora(atendimento.inicio)} ${atendimento.nome} ${atendimento.duracao}min`
        )
    })

    // Imprime a reunião de encerramento
    console.log(`${minutosParaHora(consultorio.reuniao)} Reunião de encerramento`)
    console.log("")
})

// Exporta a função para poder testar minutosParaHora no Jest
module.exports = {
    minutosParaHora
}