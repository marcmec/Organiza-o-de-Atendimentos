import unittest

from organiza_atendimentos import (
    AFTERNOON_CAPACITY,
    MIN_MEETING_START_MINUTES,
    Task,
    format_clock,
    parse_tasks,
    schedule_tasks,
    schedule_to_lines,
)


class TestOrganizaAtendimentos(unittest.TestCase):
    def test_parse_tasks_with_expresso_and_minutes(self):
        lines = [
            "Consulta de rotina 30min\n",
            "Aplicação de vacina expresso\n",
        ]
        tasks = parse_tasks(lines)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].name, "Consulta de rotina")
        self.assertEqual(tasks[0].duration_minutes, 30)
        self.assertEqual(tasks[1].name, "Aplicação de vacina")
        self.assertEqual(tasks[1].duration_minutes, 10)

    def test_schedule_fits_in_morning_and_afternoon(self):
        lines = [
            "Atendimento A 120min\n",
            "Atendimento B 90min\n",
            "Atendimento C expresso\n",
        ]
        tasks = parse_tasks(lines)
        rooms = schedule_tasks(tasks)
        self.assertEqual(len(rooms), 1)
        self.assertEqual(rooms[0].morning.used_minutes, 210)
        self.assertEqual(rooms[0].afternoon.used_minutes, 10)

    def test_meeting_starts_after_17h00_when_afternoon_ends_early(self):
        lines = [
            "Atendimento Pequeno 60min\n",
        ]
        rooms = schedule_tasks(parse_tasks(lines))
        output = schedule_to_lines(rooms)
        self.assertIn("17:01 Reunião de encerramento", output)

    def test_schedule_does_not_exceed_afternoon_capacity(self):
        lines = [
            "Atendimento Longo 120min\n",
            "Atendimento Medio 120min\n",
            "Atendimento Pequeno 30min\n",
        ]
        tasks = parse_tasks(lines)
        rooms = schedule_tasks(tasks)
        for room in rooms:
            self.assertLessEqual(room.afternoon.used_minutes, AFTERNOON_CAPACITY)

    def test_output_includes_consultorio_sections(self):
        lines = [
            "Consulta A 45min\n",
            "Consulta B 45min\n",
            "Consulta C 45min\n",
            "Consulta D 45min\n",
        ]
        rooms = schedule_tasks(parse_tasks(lines))
        output = schedule_to_lines(rooms)
        self.assertTrue(output[0].startswith("Consultório 1:"))
        self.assertTrue(any("Higienização" in line for line in output))
        self.assertTrue(any("Reunião de encerramento" in line for line in output))

    def test_format_clock(self):
        self.assertEqual(format_clock(8 * 60), "08:00")
        self.assertEqual(format_clock(17 * 60 + 1), "17:01")


if __name__ == "__main__":
    unittest.main()
