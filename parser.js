// Transforma uma linha do arquivo em um objeto de atendimento
function parseLinha(linha) {
    // Remove espaços extras e possível quebra de linha do Windows
    const limpa = linha.trim().replace("\r", "")

    // Se a linha estiver vazia, ignora
    if (limpa === "") {
        return null
    }

    // Verifica se a linha termina com a palavra "expresso"
    const ehExpresso = limpa.toLowerCase().endsWith("expresso")

    // Atendimento expresso sempre tem duração de 10 minutos
    if (ehExpresso) {
        const nome = limpa.replace(/expresso$/i, "").trim()

        return {
            nome,
            duracao: 10,
            tipo: "EXPRESSO"
        }
    }

    // Procura linhas no formato: "Nome do atendimento 90min"
    const resultado = limpa.match(/^(.*)\s+(\d+)min$/i)

    // Se não estiver no formato esperado, mostra erro
    if (!resultado) {
        throw new Error(`Linha inválida: ${linha}`)
    }

    // resultado[1] é o nome do atendimento
    // resultado[2] é a duração em minutos
    const nome = resultado[1].trim()
    const duracao = Number(resultado[2])

    return {
        nome,
        duracao,
        tipo: "NORMAL"
    }
}

module.exports = {
    parseLinha
}