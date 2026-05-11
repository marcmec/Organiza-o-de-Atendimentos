from models import Atendimento
from scheduler import organizar_atendimentos, exibir_cronograma

class App:
    @staticmethod
    def executar():
        caminho = 'atendimentos'
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                # Cria objetos e já ignora linhas vazias
                atendimentos = [Atendimento(linha) for linha in f if linha.strip()]
            
            # Ordenação Decrescente (Estratégia central do projeto)
            atendimentos.sort(key=lambda x: x.duracao, reverse=True)
            
            # Processamento
            resultado = organizar_atendimentos(atendimentos)
            
            # Saída
            exibir_cronograma(resultado)
            
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho}' não encontrado.")

if __name__ == "__main__":
    App.executar()