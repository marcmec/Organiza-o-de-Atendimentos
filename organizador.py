import math
import sys
from dataclasses import dataclass, field

MORNING_START = 8 * 60           # 08:00 em minutos
MORNING_MAX = 210                 # 08:00–11:30 = 210 min
AFTERNOON_START = 13 * 60 + 30   # 13:30 em minutos
AFTERNOON_MIN = 211               # reunião deve começar estritamente depois das 17:00
AFTERNOON_MAX = 269               # reunião deve começar estritamente antes das 18:00


@dataclass
class Appointment:
    name: str
    duration: int
    label: str


@dataclass
class Room:
    id: int
    morning: list = field(default_factory=list)
    afternoon: list = field(default_factory=list)

    @property
    def morning_used(self):
        return sum(a.duration for a in self.morning)

    @property
    def afternoon_used(self):
        return sum(a.duration for a in self.afternoon)


def parse(path):
    appointments = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, label = line.rsplit(' ', 1)
            duration = 10 if label == 'expresso' else int(label[:-3])
            appointments.append(Appointment(name, duration, label))
    return appointments


def assign(appointments, n_rooms):
    rooms = [Room(id=i + 1) for i in range(n_rooms)]

    for appt in appointments:
        # Tarde: best-fit decrescente — consultório mais preenchido que ainda comporta o atendimento
        candidates = [r for r in rooms if r.afternoon_used + appt.duration <= AFTERNOON_MAX]
        if candidates:
            max(candidates, key=lambda r: r.afternoon_used).afternoon.append(appt)
            continue

        # Manhã: consultório menos preenchido que ainda comporta o atendimento
        candidates = [r for r in rooms if r.morning_used + appt.duration <= MORNING_MAX]
        if candidates:
            min(candidates, key=lambda r: r.morning_used).morning.append(appt)
            continue

        # Nenhum consultório existente comporta: abre um novo e aloca na tarde
        new_room = Room(id=len(rooms) + 1)
        new_room.afternoon.append(appt)
        rooms.append(new_room)

    return rooms


def repair(rooms):
    for room in rooms:
        while room.afternoon_used < AFTERNOON_MIN:
            space = AFTERNOON_MAX - room.afternoon_used
            deficit = AFTERNOON_MIN - room.afternoon_used
            # Prefere o menor atendimento da manhã que cubra o déficit em um único movimento
            exact = [a for a in room.morning if deficit <= a.duration <= space]
            any_fit = [a for a in room.morning if a.duration <= space]
            if exact:
                appt = min(exact, key=lambda a: a.duration)
            elif any_fit:
                appt = max(any_fit, key=lambda a: a.duration)
            else:
                raise RuntimeError(
                    f"Consultório {room.id}: não foi possível satisfazer o mínimo da tarde "
                    f"(atual: {room.afternoon_used} min, necessário: {AFTERNOON_MIN} min)"
                )
            room.morning.remove(appt)
            room.afternoon.append(appt)


def fmt(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def print_schedule(rooms):
    for room in rooms:
        print(f"Consultório {room.id}:")
        t = MORNING_START
        for appt in room.morning:
            print(f"{fmt(t)} {appt.name} {appt.label}")
            t += appt.duration
        print("11:30 Higienização")
        t = AFTERNOON_START
        for appt in room.afternoon:
            print(f"{fmt(t)} {appt.name} {appt.label}")
            t += appt.duration
        print(f"{fmt(t)} Reunião de encerramento")
        print()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'atendimentos.txt'
    appointments = parse(path)
    appointments.sort(key=lambda a: a.duration, reverse=True)

    total = sum(a.duration for a in appointments)
    n = math.ceil(total / (MORNING_MAX + AFTERNOON_MAX))

    rooms = assign(appointments, n)
    repair(rooms)

    for room in rooms:
        assert room.morning_used <= MORNING_MAX, \
            f"Consultório {room.id}: sessão da manhã excede 210 min ({room.morning_used})"
        assert AFTERNOON_MIN <= room.afternoon_used <= AFTERNOON_MAX, \
            f"Consultório {room.id}: sessão da tarde fora do intervalo [{AFTERNOON_MIN},{AFTERNOON_MAX}] ({room.afternoon_used})"

    print_schedule(rooms)


if __name__ == '__main__':
    main()
