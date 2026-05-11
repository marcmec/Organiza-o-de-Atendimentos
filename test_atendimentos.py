import unittest
import datetime
from atendimentos import Atendimento, Consultorio, organizar_clinica, MANHA_MAX, TARDE_MAX


class TestAtendimento(unittest.TestCase):
    def test_parse_minutos(self):
        a = Atendimento("Castração de gato adulto 90min")
        self.assertEqual(a.duracao, 90)
        self.assertEqual(a.nome, "Castração de gato adulto")

    def test_parse_expresso(self):
        a = Atendimento("Aplicação de vacina antirrábica expresso")
        self.assertEqual(a.duracao, 10)
        self.assertEqual(a.nome, "Aplicação de vacina antirrábica expresso")

    def test_repr_minutos(self):
        a = Atendimento("Exame de sangue completo 30min")
        self.assertEqual(repr(a), "Exame de sangue completo 30min")

    def test_repr_expresso(self):
        a = Atendimento("Microchipagem expresso")
        self.assertEqual(repr(a), "Microchipagem expresso")


class TestConsultorio(unittest.TestCase):
    def test_manha_nao_excede_210(self):
        c = Consultorio(1)
        c.adicionar(Atendimento("A 120min"))
        c.adicionar(Atendimento("B 90min"))
        # 210 usado, não cabe mais nada na manhã
        self.assertEqual(c.usado_manha, 210)
        att = Atendimento("C expresso")
        # Deve ir para a tarde
        c.adicionar(att)
        self.assertEqual(len(c.tarde), 1)

    def test_tarde_nao_excede_270(self):
        c = Consultorio(1)
        # Enche manhã
        c.adicionar(Atendimento("A 120min"))
        c.adicionar(Atendimento("B 90min"))
        # Tarde: 269 max (reunião antes das 18:00)
        c.adicionar(Atendimento("C 120min"))
        c.adicionar(Atendimento("D 120min"))
        self.assertEqual(c.usado_tarde, 240)
        # Cabe mais 29
        self.assertTrue(c.cabe_tarde(29))
        self.assertFalse(c.cabe_tarde(30))

    def test_reuniao_minimo_17h(self):
        c = Consultorio(1)
        # Pouco na tarde
        c.adicionar_tarde(Atendimento("A 30min"))
        reuniao = c.horario_reuniao()
        self.assertEqual(reuniao.hour, 17)
        self.assertEqual(reuniao.minute, 0)

    def test_reuniao_apos_17h(self):
        c = Consultorio(1)
        # 240 min na tarde -> 13:30 + 240 = 17:30
        c.adicionar_tarde(Atendimento("A 120min"))
        c.adicionar_tarde(Atendimento("B 120min"))
        reuniao = c.horario_reuniao()
        self.assertEqual(reuniao.hour, 17)
        self.assertEqual(reuniao.minute, 30)

    def test_reuniao_antes_18h(self):
        c = Consultorio(1)
        # Máximo 270 -> 13:30 + 270 = 18:00
        c.adicionar_tarde(Atendimento("A 120min"))
        c.adicionar_tarde(Atendimento("B 120min"))
        c.adicionar_tarde(Atendimento("C 20min"))
        reuniao = c.horario_reuniao()
        self.assertLess(reuniao, datetime.datetime(2000, 1, 1, 18, 0))

    def test_consultorio_cheio_retorna_false(self):
        c = Consultorio(1)
        c.adicionar(Atendimento("A 120min"))
        c.adicionar(Atendimento("B 90min"))  # manhã cheia (210)
        c.adicionar(Atendimento("C 120min"))
        c.adicionar(Atendimento("D 120min"))
        c.adicionar(Atendimento("E 20min"))  # tarde quase cheia (260)
        # Cabe mais 9 (269-260=9), mas expresso=10 não cabe
        self.assertFalse(c.adicionar(Atendimento("F expresso")))


class TestOrganizarClinica(unittest.TestCase):
    def test_todos_alocados(self):
        dados = [
            "Castração de gato adulto 90min",
            "Aplicação de vacina antirrábica expresso",
            "Limpeza dentária em cão de pequeno porte 45min",
            "Consulta de rotina em filhote de gato 30min",
            "Exame de sangue completo 30min",
            "Cirurgia ortopédica em cão atropelado 120min",
            "Avaliação dermatológica em cão com sarna 45min",
            "Microchipagem expresso",
            "Retirada de pontos pós-cirúrgicos 30min",
            "Atendimento de emergência respiratória 60min",
            "Consulta com nutricionista veterinária 45min",
            "Ultrassonografia abdominal 60min",
            "Castração de cadela em fase reprodutiva 90min",
            "Vermifugação em ninhada de filhotes 30min",
            "Avaliação cardiológica em cão idoso 60min",
            "Curativo de ferida exposta 30min",
            "Aplicação de vacina V10 expresso",
            "Consulta comportamental para gato resgatado 45min",
            "Raio-X de pata traseira 30min",
            "Tratamento de otite em cão 30min",
            "Cirurgia de remoção de tumor cutâneo 90min",
            "Resgate emocional: socialização de gato feral 60min",
            "Avaliação ortopédica em cão com displasia 45min",
        ]
        resultado = organizar_clinica(dados)
        total_alocados = sum(len(c.manha) + len(c.tarde) for c in resultado)
        self.assertEqual(total_alocados, len(dados))

    def test_limites_respeitados(self):
        dados = [
            "Castração de gato adulto 90min",
            "Cirurgia ortopédica em cão atropelado 120min",
            "Castração de cadela em fase reprodutiva 90min",
            "Cirurgia de remoção de tumor cutâneo 90min",
            "Avaliação cardiológica em cão idoso 60min",
            "Ultrassonografia abdominal 60min",
        ]
        resultado = organizar_clinica(dados)
        for c in resultado:
            self.assertLessEqual(c.usado_manha, MANHA_MAX)
            self.assertLessEqual(c.usado_tarde, TARDE_MAX)
            reuniao = c.horario_reuniao()
            self.assertGreaterEqual(reuniao, datetime.datetime(2000, 1, 1, 17, 0))
            self.assertLess(reuniao, datetime.datetime(2000, 1, 1, 18, 0))

    def test_entrada_vazia(self):
        resultado = organizar_clinica([])
        self.assertEqual(len(resultado), 0)

    def test_um_atendimento_expresso(self):
        resultado = organizar_clinica(["Vacina expresso"])
        self.assertEqual(len(resultado), 1)
        self.assertEqual(len(resultado[0].manha), 1)

    def test_atendimento_longo_nao_excede_sessao(self):
        """Nenhum atendimento individual pode exceder a sessão de manhã ou tarde."""
        resultado = organizar_clinica(["Cirurgia complexa 120min"])
        self.assertEqual(len(resultado), 1)
        c = resultado[0]
        self.assertLessEqual(c.usado_manha, MANHA_MAX)
        self.assertLessEqual(c.usado_tarde, TARDE_MAX)

    def test_multiplos_consultorios_criados(self):
        # Muitos atendimentos longos devem gerar múltiplos consultórios
        dados = [f"Cirurgia {i} 120min" for i in range(10)]
        resultado = organizar_clinica(dados)
        self.assertGreater(len(resultado), 1)
        total = sum(len(c.manha) + len(c.tarde) for c in resultado)
        self.assertEqual(total, 10)


if __name__ == '__main__':
    unittest.main()
