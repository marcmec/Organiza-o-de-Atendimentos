import re

class Atendimento:
    def __init__(self, linha):
        self.nome_original = linha.strip()
        # Regex para limpar o nome tirando a duração do fim
        self.descricao = re.sub(r'\s(\d+min|expresso)$', '', self.nome_original, flags=re.IGNORECASE)
        self.duracao = self._extrair_duracao(linha)

    def _extrair_duracao(self, linha):
        if "expresso" in linha.lower():
            return 10
        busca = re.search(r'(\d+)min', linha)
        if busca:
            return int(busca.group(1))
        return 0

class Consultorio:
    def __init__(self, id_numero):
        self.id = id_numero
        self.sessao_manha = []
        self.sessao_tarde = []
        self.minutos_manha = 0
        self.minutos_tarde = 0
        
        # Regras de negócio centralizadas
        self.LIMITE_MANHA = 210      # 08:00 às 11:30
        self.LIMITE_TARDE_MAX = 260  # 13:30 às 17:50, terminando antes das 18:00

    def pode_receber_manha(self, duracao):
        return self.minutos_manha + duracao <= self.LIMITE_MANHA

    def pode_receber_tarde(self, duracao):
        return self.minutos_tarde + duracao <= self.LIMITE_TARDE_MAX