"""
Suite de testes para o agendador de atendimentos clínicos.
Execute com:  pytest test_agendador.py -v
"""

import pytest
from agendador import (
    Atendimento, Consultorio, escalonar, ler_atendimentos, SESSION_DURATION
)
import os
import tempfile


# ──────────────────────────────────────────────
# Fixtures de atendimentos reutilizáveis
# ──────────────────────────────────────────────

def make(id, duracao, tipo="normal", paciente="Paciente"):
    return Atendimento(id, paciente, duracao, tipo)


# ──────────────────────────────────────────────
# Testes: Atendimento (validação de dados)
# ──────────────────────────────────────────────

class TestAtendimento:
    def test_criacao_valida_normal(self):
        a = Atendimento(1, "Ana", 30, "normal")
        assert a.id == 1
        assert a.duracao == 30
        assert a.tipo == "normal"

    def test_criacao_valida_expresso(self):
        a = Atendimento(2, "Bob", 10, "expresso")
        assert a.tipo == "expresso"

    def test_duracao_zero_invalida(self):
        with pytest.raises(ValueError, match="duração deve ser positiva"):
            Atendimento(1, "X", 0, "normal")

    def test_duracao_negativa_invalida(self):
        with pytest.raises(ValueError, match="duração deve ser positiva"):
            Atendimento(1, "X", -5, "normal")

    def test_tipo_invalido(self):
        with pytest.raises(ValueError, match="tipo inválido"):
            Atendimento(1, "X", 30, "urgente")

    def test_duracao_excede_sessao(self):
        with pytest.raises(ValueError, match="excede a sessão"):
            Atendimento(1, "X", SESSION_DURATION + 1, "normal")

    def test_duracao_igual_sessao_valida(self):
        a = Atendimento(1, "X", SESSION_DURATION, "normal")
        assert a.duracao == SESSION_DURATION


# ──────────────────────────────────────────────
# Testes: Consultório
# ──────────────────────────────────────────────

class TestConsultorio:
    def test_tempo_inicial(self):
        c = Consultorio(1)
        assert c.tempo_disponivel == SESSION_DURATION
        assert c.tempo_usado == 0

    def test_pode_atender_com_espaco(self):
        c = Consultorio(1)
        a = make(1, 60)
        assert c.pode_atender(a) is True

    def test_nao_pode_atender_sem_espaco(self):
        c = Consultorio(1)
        c.alocar(make(1, SESSION_DURATION - 10))
        assert c.pode_atender(make(2, 20)) is False

    def test_pode_atender_exatamente_o_espaco(self):
        c = Consultorio(1)
        c.alocar(make(1, 400))
        assert c.pode_atender(make(2, 80)) is True  # 400+80=480

    def test_alocacao_atualiza_tempo(self):
        c = Consultorio(1)
        c.alocar(make(1, 60))
        assert c.tempo_disponivel == SESSION_DURATION - 60
        assert c.tempo_usado == 60

    def test_alocacao_multipla(self):
        c = Consultorio(1)
        c.alocar(make(1, 60))
        c.alocar(make(2, 90))
        assert c.tempo_usado == 150
        assert len(c.atendimentos) == 2

    def test_alocar_sem_espaco_lanca_excecao(self):
        c = Consultorio(1)
        c.alocar(make(1, SESSION_DURATION))
        with pytest.raises(RuntimeError):
            c.alocar(make(2, 10))


# ──────────────────────────────────────────────
# Testes: Regras de negócio do escalonador
# ──────────────────────────────────────────────

class TestEscalonador:
    def test_lista_vazia(self):
        resultado = escalonar([])
        assert resultado == []

    def test_atendimento_unico(self):
        resultado = escalonar([make(1, 60)])
        assert len(resultado) == 1

    def test_todos_cabem_em_um_consultorio(self):
        # 4 × 30 min = 120 min < 480
        atendimentos = [make(i, 30) for i in range(1, 5)]
        resultado = escalonar(atendimentos)
        assert len(resultado) == 1

    def test_consultorio_exatamente_cheio(self):
        # 8 × 60 = 480 = SESSION_DURATION
        atendimentos = [make(i, 60) for i in range(1, 9)]
        resultado = escalonar(atendimentos)
        assert len(resultado) == 1
        assert resultado[0].tempo_disponivel == 0

    def test_dois_consultorios_necessarios(self):
        # 9 × 60 = 540 > 480 → precisa de 2
        atendimentos = [make(i, 60) for i in range(1, 10)]
        resultado = escalonar(atendimentos)
        assert len(resultado) == 2

    def test_nenhum_atendimento_excede_sessao(self):
        atendimentos = [make(i, 60) for i in range(1, 10)]
        resultado = escalonar(atendimentos)
        for c in resultado:
            assert c.tempo_usado <= SESSION_DURATION

    def test_todos_atendimentos_alocados(self):
        atendimentos = [make(i, 45) for i in range(1, 13)]
        resultado = escalonar(atendimentos)
        total_alocados = sum(len(c.atendimentos) for c in resultado)
        assert total_alocados == 12

    def test_nenhum_atendimento_perdido(self):
        """IDs de entrada == IDs de saída."""
        atendimentos = [make(i, 30 + i * 5) for i in range(1, 8)]
        ids_entrada = {a.id for a in atendimentos}
        resultado = escalonar(atendimentos)
        ids_saida = {a.id for c in resultado for a in c.atendimentos}
        assert ids_entrada == ids_saida


# ──────────────────────────────────────────────
# Testes: Tratamento de expressos
# ──────────────────────────────────────────────

class TestExpressos:
    def test_expressos_sao_alocados(self):
        exp = [make(i, 10, "expresso") for i in range(1, 5)]
        resultado = escalonar(exp)
        total = sum(len(c.atendimentos) for c in resultado)
        assert total == 4

    def test_expressos_e_normais_juntos(self):
        atendimentos = [
            make(1, 120, "normal"),
            make(2, 10,  "expresso"),
            make(3, 10,  "expresso"),
            make(4, 10,  "expresso"),
        ]
        resultado = escalonar(atendimentos)
        total = sum(len(c.atendimentos) for c in resultado)
        assert total == 4

    def test_muitos_expressos_cabem_em_poucos_consultorios(self):
        # 48 × 10 min = 480 min → tudo num único consultório
        exp = [make(i, 10, "expresso") for i in range(1, 49)]
        resultado = escalonar(exp)
        assert len(resultado) == 1

    def test_consultorio_cheio_por_expressos_abre_outro(self):
        # 49 × 10 = 490 > 480 → precisa de 2
        exp = [make(i, 10, "expresso") for i in range(1, 50)]
        resultado = escalonar(exp)
        assert len(resultado) == 2


# ──────────────────────────────────────────────
# Testes: Leitura de arquivo
# ──────────────────────────────────────────────

class TestLeituraArquivo:
    def _escrever_temp(self, conteudo: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                       delete=False, encoding="utf-8")
        f.write(conteudo)
        f.close()
        return f.name

    def test_leitura_simples(self):
        path = self._escrever_temp("2\n1,Ana,30,normal\n2,Bob,10,expresso\n")
        atendimentos = ler_atendimentos(path)
        os.unlink(path)
        assert len(atendimentos) == 2
        assert atendimentos[0].paciente == "Ana"
        assert atendimentos[1].tipo == "expresso"

    def test_arquivo_inexistente(self):
        with pytest.raises(FileNotFoundError):
            ler_atendimentos("nao_existe.txt")

    def test_contagem_incorreta(self):
        path = self._escrever_temp("5\n1,Ana,30,normal\n")  # diz 5, tem 1
        with pytest.raises(ValueError, match="foram lidos"):
            ler_atendimentos(path)
        os.unlink(path)

    def test_formato_invalido(self):
        path = self._escrever_temp("1\nAna 30 normal\n")  # sem vírgulas
        with pytest.raises((ValueError, IndexError)):
            ler_atendimentos(path)
        os.unlink(path)

    def test_leitura_arquivo_principal(self):
        """Testa que atendimentos.txt é lido sem erros."""
        if os.path.exists("atendimentos.txt"):
            atendimentos = ler_atendimentos("atendimentos.txt")
            assert len(atendimentos) > 0

    def test_leitura_segunda_entrada(self):
        """Robustez: testa atendimentos2.txt."""
        if os.path.exists("atendimentos2.txt"):
            atendimentos = ler_atendimentos("atendimentos2.txt")
            resultado = escalonar(atendimentos)
            total = sum(len(c.atendimentos) for c in resultado)
            assert total == len(atendimentos)


# ──────────────────────────────────────────────
# Testes de integração
# ──────────────────────────────────────────────

class TestIntegracao:
    def test_caso_real_arquivo_principal(self):
        """Executa o fluxo completo com atendimentos.txt."""
        if not os.path.exists("atendimentos.txt"):
            pytest.skip("atendimentos.txt não encontrado")
        atendimentos = ler_atendimentos("atendimentos.txt")
        resultado = escalonar(atendimentos)
        # Todos alocados
        total = sum(len(c.atendimentos) for c in resultado)
        assert total == len(atendimentos)
        # Nenhum consultório estourou a capacidade
        for c in resultado:
            assert c.tempo_usado <= SESSION_DURATION

    def test_caso_real_segunda_entrada(self):
        if not os.path.exists("atendimentos2.txt"):
            pytest.skip("atendimentos2.txt não encontrado")
        atendimentos = ler_atendimentos("atendimentos2.txt")
        resultado = escalonar(atendimentos)
        total = sum(len(c.atendimentos) for c in resultado)
        assert total == len(atendimentos)
        for c in resultado:
            assert c.tempo_usado <= SESSION_DURATION

    def test_resultado_determinístico(self):
        """Mesma entrada → mesma saída."""
        atendimentos = [make(i, 30 + (i % 5) * 20) for i in range(1, 11)]
        r1 = escalonar(atendimentos)
        r2 = escalonar(atendimentos)
        assert len(r1) == len(r2)
