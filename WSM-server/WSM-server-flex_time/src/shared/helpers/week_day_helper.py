from datetime import date


def is_able_to_work(data: date, work_days: str) -> bool:
    if len(work_days) != 7 or not all(c in '01' for c in work_days):
        raise ValueError("Dias das semana de trabalho deve conter 7 caracteres com '0' ou '1' (domingo a sábado)")

    week_day = data.weekday()  # 0 = segunda, ..., 6 = domingo
    idx = (week_day + 1) % 7  # converte para 0=domingo, ..., 6=sábado

    return work_days[idx] == '1'