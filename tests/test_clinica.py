"""Suíte de testes da organização de atendimentos.

Rodar a partir da raiz do projeto:
    python -m unittest discover -s tests
ou simplesmente:
    python tests/test_clinica.py
"""

import os
import sys
import unittest
from collections import Counter

# Garante que o pacote `clinica` é encontrado, independente de onde se roda.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from clinica.parser import parse_linha, parse_texto, carregar
from clinica.escalonador import organizar, numero_minimo_consultorios
from clinica.relatorio import formatar_horario, formatar_agenda
from clinica.modelos import Atendimento
from clinica.regras import (
    CAP_MANHA,
    CAP_TARDE,
    MIN_TARDE,
    INICIO_TARDE,
    HIGIENIZACAO,
    EXPRESSO_MIN,
    REUNIAO_INICIO_MIN,
    REUNIAO_INICIO_MAX,
)

# Entrada oficial do desafio.
ENTRADA_OFICIAL = """\
Castração de gato adulto 90min
Aplicação de vacina antirrábica expresso
Limpeza dentária em cão de pequeno porte 45min
Consulta de rotina em filhote de gato 30min
Exame de sangue completo 30min
Cirurgia ortopédica em cão atropelado 120min
Avaliação dermatológica em cão com sarna 45min
Microchipagem expresso
Retirada de pontos pós-cirúrgicos 30min
Atendimento de emergência respiratória 60min
Consulta com nutricionista veterinária 45min
Ultrassonografia abdominal 60min
Castração de cadela em fase reprodutiva 90min
Vermifugação em ninhada de filhotes 30min
Avaliação cardiológica em cão idoso 60min
Curativo de ferida exposta 30min
Aplicação de vacina V10 expresso
Consulta comportamental para gato resgatado 45min
Raio-X de pata traseira 30min
Tratamento de otite em cão 30min
Cirurgia de remoção de tumor cutâneo 90min
Resgate emocional: socialização de gato feral 60min
Avaliação ortopédica em cão com displasia 45min
"""

# Segunda entrada "semelhante" — usada para o critério de ROBUSTEZ
# (o programa precisa funcionar com uma entrada parecida na apresentação).
ENTRADA_SEMELHANTE = """\
Castração de gato filhote 60min
Vacina polivalente expresso
Consulta clínica geral 30min
Cirurgia de hérnia 120min
Exame de fezes 30min
Aplicação de vermífugo expresso
Limpeza de tártaro 45min
Avaliação neurológica 60min
Ultrassom gestacional 45min
Curativo simples 30min
Cirurgia de castração de cadela 90min
Consulta dermatológica 45min
Raspado de pele 30min
Microchipagem de cão expresso
Atendimento de emergência 90min
Consulta cardiológica 60min
Sutura de corte profundo 45min
Nebulização 30min
Cirurgia oftálmica 90min
Avaliação geriátrica 60min
"""


def validar_agenda(caso, consultorios, atendimentos_originais):
    """Verifica TODAS as regras da clínica sobre uma agenda montada.

    Reaproveitado por vários testes para não repetir as asserções.
    """
    # 1) Nenhum atendimento perdido ou duplicado.
    def chave(a):
        return (a.nome, a.duracao, a.expresso)

    esperados = Counter(chave(a) for a in atendimentos_originais)
    agendados = Counter(
        chave(a)
        for c in consultorios
        for s in c.sessoes
        for a in s.atendimentos
    )
    caso.assertEqual(esperados, agendados, "atendimentos perdidos ou duplicados")

    for c in consultorios:
        # 2) Manhã termina até as 11:30 (ocupação <= 210).
        caso.assertLessEqual(c.manha.ocupacao, CAP_MANHA,
                             f"manhã do consultório {c.numero} passa de 11:30")
        caso.assertLessEqual(c.manha.fim, HIGIENIZACAO)

        # 3) Tarde termina dentro da janela da reunião [17:00, 18:00).
        caso.assertGreaterEqual(c.tarde.ocupacao, MIN_TARDE,
                                f"tarde do consultório {c.numero} acaba antes das 17:00")
        caso.assertLess(c.tarde.ocupacao, CAP_TARDE,
                        f"tarde do consultório {c.numero} acaba 18:00 ou depois")

        # 4) Horário concreto da reunião dentro da janela.
        reuniao = c.tarde.fim
        caso.assertGreaterEqual(reuniao, REUNIAO_INICIO_MIN)
        caso.assertLess(reuniao, REUNIAO_INICIO_MAX)

        # 5) A tarde sempre começa às 13:30.
        caso.assertEqual(c.tarde.inicio, INICIO_TARDE)


class TestParser(unittest.TestCase):
    def test_atendimento_com_minutos(self):
        at = parse_linha("Castração de gato adulto 90min")
        self.assertEqual(at.nome, "Castração de gato adulto")
        self.assertEqual(at.duracao, 90)
        self.assertFalse(at.expresso)

    def test_expresso_vale_dez_minutos(self):
        at = parse_linha("Microchipagem expresso")
        self.assertEqual(at.duracao, EXPRESSO_MIN)
        self.assertEqual(at.duracao, 10)
        self.assertTrue(at.expresso)
        self.assertEqual(at.rotulo_duracao, "expresso")

    def test_nome_com_numero_nao_quebra_o_parser(self):
        # "V10" faz parte do nome; a duração é o último token ("expresso").
        at = parse_linha("Aplicação de vacina V10 expresso")
        self.assertEqual(at.nome, "Aplicação de vacina V10")
        self.assertTrue(at.expresso)

    def test_nome_com_dois_pontos(self):
        at = parse_linha("Resgate emocional: socialização de gato feral 60min")
        self.assertEqual(at.nome, "Resgate emocional: socialização de gato feral")
        self.assertEqual(at.duracao, 60)

    def test_linha_em_branco_vira_none(self):
        self.assertIsNone(parse_linha("   "))

    def test_linha_invalida_levanta_erro(self):
        with self.assertRaises(ValueError):
            parse_linha("Atendimento sem duracao")

    def test_parse_texto_ignora_linhas_vazias(self):
        ats = parse_texto("Consulta 30min\n\n\nMicrochipagem expresso\n")
        self.assertEqual(len(ats), 2)


class TestEntradaOficial(unittest.TestCase):
    def setUp(self):
        self.atendimentos = parse_texto(ENTRADA_OFICIAL)
        self.consultorios = organizar(self.atendimentos)

    def test_quantidade_de_atendimentos(self):
        self.assertEqual(len(self.atendimentos), 23)

    def test_duracao_total(self):
        self.assertEqual(sum(a.duracao for a in self.atendimentos), 1095)

    def test_usa_tres_consultorios(self):
        # 1095 / 479 = 2.28 -> pelo menos 3 consultórios.
        self.assertEqual(numero_minimo_consultorios(1095), 3)
        self.assertEqual(len(self.consultorios), 3)

    def test_agenda_respeita_todas_as_regras(self):
        validar_agenda(self, self.consultorios, self.atendimentos)


class TestRobustez(unittest.TestCase):
    """Critério de robustez: uma segunda entrada semelhante também funciona."""

    def test_entrada_semelhante_gera_agenda_valida(self):
        atendimentos = parse_texto(ENTRADA_SEMELHANTE)
        consultorios = organizar(atendimentos)
        self.assertGreaterEqual(len(consultorios), 1)
        validar_agenda(self, consultorios, atendimentos)


class TestCasosLimite(unittest.TestCase):
    def test_lista_vazia(self):
        self.assertEqual(organizar([]), [])

    def test_um_unico_atendimento_grande_preenche_uma_tarde(self):
        # 240 min cabe sozinho numa tarde (210 <= 240 < 270): 1 consultório.
        ats = [Atendimento("Cirurgia longa", 240)]
        consultorios = organizar(ats)
        self.assertEqual(len(consultorios), 1)
        validar_agenda(self, consultorios, ats)

    def test_entrada_pequena_demais_e_infazivel(self):
        # 30 min não dá para preencher uma tarde até 210 min -> sem agenda válida.
        with self.assertRaises(ValueError):
            organizar([Atendimento("Consulta rápida", 30)])

    def test_numero_minimo_consultorios(self):
        self.assertEqual(numero_minimo_consultorios(0), 0)
        self.assertEqual(numero_minimo_consultorios(1), 1)
        self.assertEqual(numero_minimo_consultorios(479), 1)
        self.assertEqual(numero_minimo_consultorios(480), 2)
        self.assertEqual(numero_minimo_consultorios(1095), 3)


class TestRelatorio(unittest.TestCase):
    def test_formatar_horario(self):
        self.assertEqual(formatar_horario(8 * 60), "08:00")
        self.assertEqual(formatar_horario(11 * 60 + 30), "11:30")
        self.assertEqual(formatar_horario(17 * 60 + 45), "17:45")

    def test_saida_contem_marcos_fixos(self):
        atendimentos = parse_texto(ENTRADA_OFICIAL)
        texto = formatar_agenda(organizar(atendimentos))
        self.assertIn("Consultório 1:", texto)
        self.assertIn("11:30 Higienização", texto)
        self.assertIn("Reunião de encerramento", texto)
        # a manhã sempre começa às 08:00 e a tarde às 13:30
        self.assertIn("08:00 ", texto)
        self.assertIn("13:30 ", texto)

    def test_horarios_da_manha_sao_sequenciais(self):
        # Monta um caso controlado e confere que o relógio anda certinho.
        ats = [
            Atendimento("Cirurgia A", 120),
            Atendimento("Consulta B", 90),   # tarde: 120+90 = 210 (>=210, <270)
            Atendimento("Exame C", 60),
            Atendimento("Curativo D", 30),    # manhã: 60 + 30 = 90
        ]
        texto = formatar_agenda(organizar(ats))
        # A tarde recebe os maiores (Fase 1): 13:30 Cirurgia A, 15:30 Consulta B.
        self.assertIn("13:30 Cirurgia A 120min", texto)
        self.assertIn("15:30 Consulta B 90min", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
