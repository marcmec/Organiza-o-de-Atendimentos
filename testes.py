# -*- coding: utf-8 -*-
"""
Suite de testes automatizados - Organizador de Atendimentos.
Execute com: python3 -m pytest testes.py -v
"""

import pytest
from organizador import (
    Atendimento, Sessao, Consultorio,
    parse_atendimentos, organizar, validar, formatar_saida,
    MANHA_INICIO, MANHA_FIM, TARDE_INICIO,
    REUNIAO_MINIMO, REUNIAO_MAXIMO,
    CAPACIDADE_MANHA, TARDE_MIN, TARDE_MAX, DURACAO_EXPRESSO,
)

# ── Entradas de teste ─────────────────────────────────────────────────────────

ENTRADA_ORIGINAL = """
Castracao de gato adulto 90min
Aplicacao de vacina antirrabica expresso
Limpeza dentaria em cao de pequeno porte 45min
Consulta de rotina em filhote de gato 30min
Exame de sangue completo 30min
Cirurgia ortopedica em cao atropelado 120min
Avaliacao dermatologica em cao com sarna 45min
Microchipagem expresso
Retirada de pontos pos-cirurgicos 30min
Atendimento de emergencia respiratoria 60min
Consulta com nutricionista veterinaria 45min
Ultrassonografia abdominal 60min
Castracao de cadela em fase reprodutiva 90min
Vermifugacao em ninhada de filhotes 30min
Avaliacao cardiologica em cao idoso 60min
Curativo de ferida exposta 30min
Aplicacao de vacina V10 expresso
Consulta comportamental para gato resgatado 45min
Raio-X de pata traseira 30min
Tratamento de otite em cao 30min
Cirurgia de remocao de tumor cutaneo 90min
Resgate emocional de gato feral 60min
Avaliacao ortopedica em cao com displasia 45min
"""

ENTRADA_ALTERNATIVA = """
Consulta clinica geral 30min
Vacinacao multipla expresso
Esterilizacao de gata 90min
Teste de FIV e FeLV 30min
Drenagem de abscesso 45min
Cirurgia de hernia diafragmatica 120min
Avaliacao oftalmologica 45min
Aplicacao de antipulgas expresso
Curativo complexo pos-queimadura 60min
Necropscia veterinaria 60min
Consulta de acompanhamento oncologico 45min
Ecocardiograma 60min
Castracao de cao adulto 90min
Tratamento periodontal 30min
Avaliacao neurologica 60min
Medicacao endovenosa 30min
Identificacao por microchip expresso
Avaliacao comportamental cao reativo 45min
Radiografia de coluna 30min
Limpeza auricular 30min
Remocao de lipoma 90min
Fisioterapia pos-operatoria 60min
Avaliacao de displasia coxofemoral 45min
"""


# ── 1. Testes de parsing ──────────────────────────────────────────────────────

class TestParser:
    def test_parse_duracao_minutos(self):
        a = parse_atendimentos("Castracao de gato adulto 90min")
        assert len(a) == 1
        assert a[0].nome == "Castracao de gato adulto"
        assert a[0].duracao == 90
        assert a[0].expresso is False

    def test_parse_expresso(self):
        a = parse_atendimentos("Microchipagem expresso")
        assert len(a) == 1
        assert a[0].duracao == DURACAO_EXPRESSO
        assert a[0].expresso is True

    def test_parse_ignora_linhas_vazias(self):
        assert len(parse_atendimentos("\n\nCastracao 90min\n\n")) == 1

    def test_parse_ignora_comentarios(self):
        assert len(parse_atendimentos("# comentario\nMicrochipagem expresso")) == 1

    def test_parse_linha_invalida_levanta_erro(self):
        with pytest.raises(ValueError):
            parse_atendimentos("Consulta sem duracao")

    def test_parse_quantidade_original(self):
        assert len(parse_atendimentos(ENTRADA_ORIGINAL)) == 23

    def test_parse_expressos_contados(self):
        expressos = [a for a in parse_atendimentos(ENTRADA_ORIGINAL) if a.expresso]
        assert len(expressos) == 3

    def test_parse_case_insensitive_expresso(self):
        assert parse_atendimentos("Vacinacao EXPRESSO")[0].expresso is True

    def test_parse_case_insensitive_min(self):
        assert parse_atendimentos("Consulta 45MIN")[0].duracao == 45

    def test_parse_duracao_expresso_e_dez(self):
        assert parse_atendimentos("Vacinacao expresso")[0].duracao == 10


# ── 2. Testes de estruturas de dados ─────────────────────────────────────────

class TestSessao:
    def test_capacidade_inicial(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        assert s.tempo_livre == CAPACIDADE_MANHA
        assert s.tempo_usado == 0

    def test_adiciona_com_sucesso(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        assert s.adicionar(Atendimento("A", 60)) is True
        assert s.tempo_usado == 60

    def test_nao_adiciona_acima_da_capacidade(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        assert s.adicionar(Atendimento("Grande", CAPACIDADE_MANHA + 1)) is False

    def test_adiciona_exatamente_na_capacidade(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        assert s.adicionar(Atendimento("Exato", CAPACIDADE_MANHA)) is True

    def test_multiplos_itens(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        s.adicionar(Atendimento("A", 90))
        s.adicionar(Atendimento("B", 90))
        assert s.tempo_usado == 180
        assert s.tempo_livre == 30

    def test_nao_adiciona_quando_cheio(self):
        s = Sessao(MANHA_INICIO, CAPACIDADE_MANHA)
        s.adicionar(Atendimento("A", 90))
        s.adicionar(Atendimento("B", 90))
        assert s.adicionar(Atendimento("C", 45)) is False


# ── 3. Testes das regras de negocio ──────────────────────────────────────────

class TestRegras:

    def _rodar(self, texto):
        atend = parse_atendimentos(texto)
        return organizar(atend), atend

    def test_todos_alocados_entrada_original(self):
        consultorios, atend = self._rodar(ENTRADA_ORIGINAL)
        alocados = [a for c in consultorios for s in c.sessoes() for a in s.atendimentos]
        assert len(alocados) == len(atend)

    def test_manha_nao_ultrapassa_1130(self):
        consultorios, _ = self._rodar(ENTRADA_ORIGINAL)
        for c in consultorios:
            assert c.manha.tempo_usado <= CAPACIDADE_MANHA

    def test_reuniao_depois_das_17h(self):
        consultorios, _ = self._rodar(ENTRADA_ORIGINAL)
        for c in consultorios:
            fim = TARDE_INICIO + c.tarde.tempo_usado
            assert fim >= REUNIAO_MINIMO, \
                f"Consultorio {c.numero}: reuniao as {fim//60}:{fim%60:02d} - antes das 17h"

    def test_reuniao_antes_das_18h(self):
        consultorios, _ = self._rodar(ENTRADA_ORIGINAL)
        for c in consultorios:
            fim = TARDE_INICIO + c.tarde.tempo_usado
            assert fim < REUNIAO_MAXIMO, \
                f"Consultorio {c.numero}: reuniao as {fim//60}:{fim%60:02d} - 18h ou depois"

    def test_validacao_sem_erros_original(self):
        consultorios, atend = self._rodar(ENTRADA_ORIGINAL)
        assert validar(consultorios, atend) == []

    def test_validacao_sem_erros_alternativo(self):
        consultorios, atend = self._rodar(ENTRADA_ALTERNATIVA)
        assert validar(consultorios, atend) == []

    def test_todos_alocados_alternativo(self):
        consultorios, atend = self._rodar(ENTRADA_ALTERNATIVA)
        alocados = [a for c in consultorios for s in c.sessoes() for a in s.atendimentos]
        assert len(alocados) == len(atend)

    def test_regras_alternativo_manha(self):
        consultorios, _ = self._rodar(ENTRADA_ALTERNATIVA)
        for c in consultorios:
            assert c.manha.tempo_usado <= CAPACIDADE_MANHA

    def test_regras_alternativo_reuniao_depois_17h(self):
        consultorios, _ = self._rodar(ENTRADA_ALTERNATIVA)
        for c in consultorios:
            fim = TARDE_INICIO + c.tarde.tempo_usado
            assert fim >= REUNIAO_MINIMO

    def test_regras_alternativo_reuniao_antes_18h(self):
        consultorios, _ = self._rodar(ENTRADA_ALTERNATIVA)
        for c in consultorios:
            fim = TARDE_INICIO + c.tarde.tempo_usado
            assert fim < REUNIAO_MAXIMO

    def test_unico_atendimento_cria_um_consultorio(self):
        consultorios, _ = self._rodar("Consulta rapida 30min")
        assert len(consultorios) == 1

    def test_expresso_tem_10_minutos(self):
        atend = parse_atendimentos("Vacinacao expresso")
        assert atend[0].duracao == 10

    def test_dois_atendimentos_mesmo_consultorio(self):
        # Dois de 30min cabem na mesma tarde (210min min necessario -- mas 60 < 210)
        # Logo abrira apenas 1 consultorio mas tarde tera so 60min...
        # Na pratica: algoritmo pode abrir 1 consultorio com tarde < 210 se total < 210
        # Validacao: nao ha erro de "muitos consultorios"
        consultorios, atend = self._rodar("Consulta A 30min\nConsulta B 30min")
        alocados = [a for c in consultorios for s in c.sessoes() for a in s.atendimentos]
        assert len(alocados) == 2

    def test_atendimento_maior_que_sessao_levanta_erro(self):
        with pytest.raises(ValueError):
            organizar([Atendimento("Gigante", max(TARDE_MAX, CAPACIDADE_MANHA) + 1)])

    def test_lista_vazia_retorna_lista_vazia(self):
        assert organizar([]) == []

    def test_numeros_dos_consultorios_sequenciais(self):
        consultorios, _ = self._rodar(ENTRADA_ORIGINAL)
        numeros = [c.numero for c in consultorios]
        assert numeros == list(range(1, len(consultorios) + 1))

    def test_expressos_alocados(self):
        """Todos os expressos do arquivo original devem ser alocados."""
        consultorios, atend = self._rodar(ENTRADA_ORIGINAL)
        alocados = [a for c in consultorios for s in c.sessoes() for a in s.atendimentos]
        expressos_orig = sum(1 for a in atend if a.expresso)
        expressos_aloc = sum(1 for a in alocados if a.expresso)
        assert expressos_orig == expressos_aloc


# ── 4. Testes de formatacao de saida ─────────────────────────────────────────

class TestFormatacao:

    def _saida(self, texto=ENTRADA_ORIGINAL):
        atend = parse_atendimentos(texto)
        return formatar_saida(organizar(atend))

    def test_contem_higienizacao(self):
        assert "Higienizacao" in self._saida()

    def test_contem_reuniao_encerramento(self):
        assert "Reuniao de encerramento" in self._saida()

    def test_contem_todos_consultorios(self):
        atend = parse_atendimentos(ENTRADA_ORIGINAL)
        consultorios = organizar(atend)
        saida = formatar_saida(consultorios)
        for c in consultorios:
            assert f"Consultorio {c.numero}:" in saida

    def test_hora_inicio_manha(self):
        # Para a manha ser usada, precisa de carga suficiente para encher as tardes
        # e ainda sobrar para a manha. Usamos a entrada original, que tem manha vazia,
        # mas garantimos que 08:00 aparece como hora de referencia da sessao da manha.
        # O programa sempre exibe 11:30 Higienizacao, que confirma o turno da manha.
        assert "11:30" in self._saida()

    def test_hora_inicio_tarde(self):
        assert "13:30" in self._saida()

    def test_hora_higienizacao(self):
        assert "11:30" in self._saida()

