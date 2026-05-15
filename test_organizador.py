import math
import os
import tempfile
import unittest

from organizador import (
    Appointment, Room,
    parse, assign, repair,
    MORNING_MAX, MORNING_START,
    AFTERNOON_MIN, AFTERNOON_MAX, AFTERNOON_START,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def _appt(duration):
    return Appointment(f'Procedimento {duration}min', duration, f'{duration}min')


def _parse_text(text):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        path = f.name
    try:
        return parse(path)
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

class TestParsing(unittest.TestCase):

    def test_expresso_vira_dez_minutos(self):
        appts = _parse_text('Aplicação de vacina expresso\n')
        self.assertEqual(appts[0].duration, 10)
        self.assertEqual(appts[0].label, 'expresso')

    def test_sufixo_min_extraido_corretamente(self):
        appts = _parse_text('Castração de gato adulto 90min\n')
        self.assertEqual(appts[0].duration, 90)
        self.assertEqual(appts[0].label, '90min')
        self.assertEqual(appts[0].name, 'Castração de gato adulto')

    def test_nome_com_dois_pontos_preservado(self):
        appts = _parse_text('Resgate emocional: socialização de gato feral 60min\n')
        self.assertEqual(appts[0].name, 'Resgate emocional: socialização de gato feral')
        self.assertEqual(appts[0].duration, 60)

    def test_nome_com_numero_no_meio(self):
        # "V10" no meio do nome não deve ser confundido com duração
        appts = _parse_text('Aplicação de vacina V10 expresso\n')
        self.assertEqual(appts[0].name, 'Aplicação de vacina V10')
        self.assertEqual(appts[0].duration, 10)

    def test_linhas_vazias_ignoradas(self):
        appts = _parse_text('\nConsulta 30min\n\nVacina expresso\n\n')
        self.assertEqual(len(appts), 2)

    def test_arquivo_completo_tem_23_atendimentos(self):
        appts = parse(os.path.join(HERE, 'atendimentos.txt'))
        self.assertEqual(len(appts), 23)

    def test_total_de_minutos_do_arquivo(self):
        appts = parse(os.path.join(HERE, 'atendimentos.txt'))
        self.assertEqual(sum(a.duration for a in appts), 1095)


# ---------------------------------------------------------------------------
# Room — propriedades calculadas
# ---------------------------------------------------------------------------

class TestRoomProperties(unittest.TestCase):

    def test_morning_used_vazio(self):
        self.assertEqual(Room(id=1).morning_used, 0)

    def test_afternoon_used_vazio(self):
        self.assertEqual(Room(id=1).afternoon_used, 0)

    def test_morning_used_soma_duracoes(self):
        room = Room(id=1, morning=[_appt(30), _appt(45)])
        self.assertEqual(room.morning_used, 75)

    def test_afternoon_used_soma_duracoes(self):
        room = Room(id=1, afternoon=[_appt(90), _appt(60)])
        self.assertEqual(room.afternoon_used, 150)


# ---------------------------------------------------------------------------
# Assign — lógica de alocação
# ---------------------------------------------------------------------------

class TestAssign(unittest.TestCase):

    def test_todos_os_atendimentos_alocados(self):
        appts = [_appt(d) for d in [90, 60, 45, 30, 10]]
        rooms = assign(sorted(appts, key=lambda a: a.duration, reverse=True), 1)
        total = sum(len(r.morning) + len(r.afternoon) for r in rooms)
        self.assertEqual(total, len(appts))

    def test_manhã_nunca_ultrapassa_210_min(self):
        appts = sorted([_appt(d) for d in [90, 90, 60, 60, 45, 30]],
                       key=lambda a: a.duration, reverse=True)
        n = math.ceil(sum(a.duration for a in appts) / (MORNING_MAX + AFTERNOON_MAX))
        for room in assign(appts, n):
            self.assertLessEqual(room.morning_used, MORNING_MAX,
                                 msg=f'Consultório {room.id}: manhã = {room.morning_used}')

    def test_tarde_nunca_ultrapassa_269_min(self):
        appts = sorted([_appt(d) for d in [120, 90, 90, 60, 45, 30]],
                       key=lambda a: a.duration, reverse=True)
        n = math.ceil(sum(a.duration for a in appts) / (MORNING_MAX + AFTERNOON_MAX))
        for room in assign(appts, n):
            self.assertLessEqual(room.afternoon_used, AFTERNOON_MAX,
                                 msg=f'Consultório {room.id}: tarde = {room.afternoon_used}')

    def test_abre_novo_consultorio_quando_necessario(self):
        # Três atendimentos de 200 min cada: o terceiro não cabe em um consultório já cheio
        appts = [_appt(200), _appt(200), _appt(200)]
        rooms = assign(appts, 1)
        self.assertGreater(len(rooms), 1)

    def test_best_fit_empacota_tarde_antes_de_abrir_nova(self):
        # Dois atendimentos de 140 min: 140+140=280 > 269, não cabem juntos na tarde
        appts = [_appt(140), _appt(140)]
        rooms = assign(appts, 2)
        tardes = [r.afternoon_used for r in rooms if r.afternoon]
        self.assertTrue(all(u == 140 for u in tardes))

    def test_n_consultórios_calculado_corretamente_para_entrada_real(self):
        appts = parse(os.path.join(HERE, 'atendimentos.txt'))
        n = math.ceil(sum(a.duration for a in appts) / (MORNING_MAX + AFTERNOON_MAX))
        self.assertEqual(n, 3)


# ---------------------------------------------------------------------------
# Repair — correção do mínimo da tarde
# ---------------------------------------------------------------------------

class TestRepair(unittest.TestCase):

    def test_repara_tarde_abaixo_do_minimo(self):
        room = Room(id=1,
                    morning=[_appt(60)],
                    afternoon=[_appt(120), _appt(80)])  # tarde = 200 < 211
        repair([room])
        self.assertGreaterEqual(room.afternoon_used, AFTERNOON_MIN)
        self.assertLessEqual(room.afternoon_used, AFTERNOON_MAX)

    def test_nao_altera_tarde_ja_satisfeita(self):
        room = Room(id=1,
                    morning=[_appt(60)],
                    afternoon=[_appt(120), _appt(100)])  # tarde = 220 ≥ 211
        antes = room.afternoon_used
        repair([room])
        self.assertEqual(room.afternoon_used, antes)

    def test_total_de_atendimentos_inalterado_apos_reparo(self):
        room = Room(id=1,
                    morning=[_appt(30), _appt(30)],
                    afternoon=[_appt(120), _appt(60)])  # tarde = 180 < 211
        total_antes = len(room.morning) + len(room.afternoon)
        repair([room])
        self.assertEqual(len(room.morning) + len(room.afternoon), total_antes)

    def test_reparo_lança_erro_quando_impossível(self):
        # Tarde = 200, manhã tem só 90 min — mover causaria tarde 290 > 269
        room = Room(id=1,
                    morning=[_appt(90)],
                    afternoon=[_appt(120), _appt(80)])
        with self.assertRaises(RuntimeError):
            repair([room])

    def test_reparo_múltiplas_salas(self):
        rooms = [
            Room(id=1, morning=[_appt(45)], afternoon=[_appt(120), _appt(60)]),  # 180 < 211
            Room(id=2, morning=[_appt(45)], afternoon=[_appt(220)]),              # 220 ≥ 211
        ]
        repair(rooms)
        self.assertGreaterEqual(rooms[0].afternoon_used, AFTERNOON_MIN)
        self.assertGreaterEqual(rooms[1].afternoon_used, AFTERNOON_MIN)  # não tocou


# ---------------------------------------------------------------------------
# Integração — pipeline completo com atendimentos.txt
# ---------------------------------------------------------------------------

class TestIntegração(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        appts = parse(os.path.join(HERE, 'atendimentos.txt'))
        appts.sort(key=lambda a: a.duration, reverse=True)
        cls.appts = appts
        n = math.ceil(sum(a.duration for a in appts) / (MORNING_MAX + AFTERNOON_MAX))
        cls.rooms = assign(appts, n)
        repair(cls.rooms)

    def test_três_consultórios_gerados(self):
        self.assertEqual(len(self.rooms), 3)

    def test_todos_os_atendimentos_presentes(self):
        alocados = [a for r in self.rooms for a in r.morning + r.afternoon]
        self.assertEqual(len(alocados), len(self.appts))

    def test_sem_atendimentos_duplicados(self):
        nomes = [a.name for r in self.rooms for a in r.morning + r.afternoon]
        self.assertEqual(len(nomes), len(set(nomes)))

    def test_soma_total_de_minutos_preservada(self):
        total_entrada = sum(a.duration for a in self.appts)
        total_alocado = sum(
            a.duration for r in self.rooms for a in r.morning + r.afternoon
        )
        self.assertEqual(total_entrada, total_alocado)

    def test_manhã_dentro_do_limite_em_todos_consultórios(self):
        for room in self.rooms:
            self.assertLessEqual(room.morning_used, MORNING_MAX,
                                 msg=f'Consultório {room.id}: manhã = {room.morning_used} min')

    def test_tarde_acima_do_mínimo_em_todos_consultórios(self):
        for room in self.rooms:
            self.assertGreaterEqual(room.afternoon_used, AFTERNOON_MIN,
                                    msg=f'Consultório {room.id}: tarde = {room.afternoon_used} min')

    def test_tarde_abaixo_do_máximo_em_todos_consultórios(self):
        for room in self.rooms:
            self.assertLessEqual(room.afternoon_used, AFTERNOON_MAX,
                                 msg=f'Consultório {room.id}: tarde = {room.afternoon_used} min')

    def test_reunião_começa_depois_das_17h(self):
        for room in self.rooms:
            inicio_reuniao = AFTERNOON_START + room.afternoon_used
            self.assertGreater(inicio_reuniao, 17 * 60,
                               msg=f'Consultório {room.id}: reunião às {inicio_reuniao} min (≤ 17:00)')

    def test_reunião_começa_antes_das_18h(self):
        for room in self.rooms:
            inicio_reuniao = AFTERNOON_START + room.afternoon_used
            self.assertLess(inicio_reuniao, 18 * 60,
                            msg=f'Consultório {room.id}: reunião às {inicio_reuniao} min (≥ 18:00)')


if __name__ == '__main__':
    unittest.main(verbosity=2)
