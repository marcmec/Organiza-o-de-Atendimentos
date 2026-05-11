from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

MORNING_CAPACITY = 210
AFTERNOON_CAPACITY = 269
MORNING_START_MINUTES = 8 * 60
AFTERNOON_START_MINUTES = 13 * 60 + 30
MIN_MEETING_START_MINUTES = 17 * 60 + 1
MAX_MEETING_START_MINUTES = 18 * 60 - 1

DURATION_PATTERN = re.compile(r"^(?P<label>expresso|\d+min)$", re.IGNORECASE)


@dataclass
class Task:
    name: str
    duration_minutes: int
    duration_label: str

    @classmethod
    def from_line(cls, line: str) -> Task:
        stripped = line.strip()
        if not stripped:
            raise ValueError("Linha vazia não pode ser convertida em atendimento")

        parts = stripped.rsplit(" ", 1)
        if len(parts) != 2:
            raise ValueError(f"Formato inválido de atendimento: {line!r}")

        name, label = parts
        label = label.lower()
        match = DURATION_PATTERN.match(label)
        if not match:
            raise ValueError(f"Duração inválida no atendimento: {line!r}")

        if label == "expresso":
            duration = 10
        else:
            duration = int(label[:-3])

        if duration <= 0:
            raise ValueError(f"Duração deve ser positiva: {line!r}")

        return cls(name=name, duration_minutes=duration, duration_label=label)


@dataclass
class Session:
    start_minutes: int
    capacity: int
    tasks: List[Task] = field(default_factory=list)
    used_minutes: int = 0

    def can_fit(self, task: Task) -> bool:
        return self.used_minutes + task.duration_minutes <= self.capacity

    def add(self, task: Task) -> None:
        if not self.can_fit(task):
            raise ValueError(f"Não cabe o atendimento {task.name} na sessão")
        self.tasks.append(task)
        self.used_minutes += task.duration_minutes

    def slack_after(self, task: Task) -> int:
        return self.capacity - (self.used_minutes + task.duration_minutes)

    @property
    def end_minutes(self) -> int:
        return self.start_minutes + self.used_minutes


@dataclass
class Room:
    morning: Session = field(default_factory=lambda: Session(start_minutes=MORNING_START_MINUTES, capacity=MORNING_CAPACITY))
    afternoon: Session = field(default_factory=lambda: Session(start_minutes=AFTERNOON_START_MINUTES, capacity=AFTERNOON_CAPACITY))


def parse_tasks(lines: Iterable[str]) -> List[Task]:
    return [Task.from_line(line) for line in lines if line.strip()]


def choose_best_session(room: Room, task: Task) -> Optional[Tuple[str, int]]:
    best: Optional[Tuple[str, int]] = None
    for session_name in ("morning", "afternoon"):
        session = getattr(room, session_name)
        if session.can_fit(task):
            slack = session.slack_after(task)
            if best is None or slack < best[1] or (slack == best[1] and session_name == "morning"):
                best = (session_name, slack)
    return best


def schedule_tasks(tasks: List[Task]) -> List[Room]:
    tasks_sorted = sorted(tasks, key=lambda t: t.duration_minutes, reverse=True)
    rooms: List[Room] = []

    for task in tasks_sorted:
        best_choice: Optional[Tuple[Room, str, int]] = None
        for room in rooms:
            choice = choose_best_session(room, task)
            if choice is not None:
                session_name, slack = choice
                if best_choice is None or slack < best_choice[2] or (
                    slack == best_choice[2] and session_name == "morning" and best_choice[1] == "afternoon"
                ):
                    best_choice = (room, session_name, slack)

        if best_choice:
            room, session_name, _ = best_choice
            getattr(room, session_name).add(task)
            continue

        room = Room()
        if task.duration_minutes <= MORNING_CAPACITY:
            room.morning.add(task)
        elif task.duration_minutes <= AFTERNOON_CAPACITY:
            room.afternoon.add(task)
        else:
            raise ValueError(f"Atendimento muito longo para qualquer sessão: {task.name} ({task.duration_minutes} min)")
        rooms.append(room)

    return rooms


def format_clock(minutes: int) -> str:
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def schedule_to_lines(rooms: List[Room]) -> List[str]:
    lines: List[str] = []
    for index, room in enumerate(rooms, start=1):
        lines.append(f"Consultório {index}:")
        current = room.morning.start_minutes
        for task in room.morning.tasks:
            lines.append(f"{format_clock(current)} {task.name} {task.duration_label}")
            current += task.duration_minutes
        lines.append("11:30 Higienização")
        lines.append("")
        current = room.afternoon.start_minutes
        for task in room.afternoon.tasks:
            lines.append(f"{format_clock(current)} {task.name} {task.duration_label}")
            current += task.duration_minutes
        meeting_start = max(current, MIN_MEETING_START_MINUTES)
        if meeting_start > MAX_MEETING_START_MINUTES:
            raise ValueError(f"Não é possível agendar a reunião de encerramento no consultório {index}")
        lines.append(f"{format_clock(meeting_start)} Reunião de encerramento")
        if index < len(rooms):
            lines.append("")
    return lines


def read_input_file(path: str) -> List[str]:
    with open(path, encoding="utf-8") as handle:
        return handle.readlines()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organizador de atendimentos para clínica veterinária")
    parser.add_argument("input", nargs="?", default="atendimentos", help="Arquivo de atendimentos de entrada")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        lines = read_input_file(args.input)
    except FileNotFoundError:
        raise SystemExit(f"Arquivo não encontrado: {args.input}")

    tasks = parse_tasks(lines)
    if not tasks:
        raise SystemExit("Nenhum atendimento encontrado no arquivo de entrada")

    rooms = schedule_tasks(tasks)
    output_lines = schedule_to_lines(rooms)
    print("\n".join(output_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
