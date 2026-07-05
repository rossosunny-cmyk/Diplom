from datetime import datetime, timedelta, timezone
from uuid import uuid4


MAX_TITLE_LENGTH = 40


def get_event_title(prefix: str = "Autotest event") -> str:
    """
    Сгенерировать уникальное название события.

    Args:
        prefix: префикс названия события.

    Returns:
        Уникальное название события длиной не более 40 символов.
    """
    suffix = uuid4().hex[:8]
    title = f"{prefix} {suffix}"

    return title[:MAX_TITLE_LENGTH]


def get_title_with_length(length: int) -> str:
    """
    Сгенерировать название события заданной длины.

    Args:
        length: нужная длина строки.

    Returns:
        Название события заданной длины.
    """
    return "А" * length


def get_max_length_title() -> str:
    """
    Получить название события максимальной допустимой длины.

    Returns:
        Строка длиной 40 символов.
    """
    return get_title_with_length(MAX_TITLE_LENGTH)


def get_too_long_title() -> str:
    """
    Получить название события длиной больше допустимой.

    Returns:
        Строка длиной 41 символ.
    """
    return get_title_with_length(MAX_TITLE_LENGTH + 1)


def get_ui_date(days_from_now: int = 0) -> str:
    """
    Получить дату для ввода в UI.

    Args:
        days_from_now: количество дней от текущей даты.

    Returns:
        Дата в формате ДД.ММ.ГГГГ.
    """
    tz = timezone(timedelta(hours=3))
    date = datetime.now(tz) + timedelta(days=days_from_now)

    return date.strftime("%d.%m.%Y")


def get_event_time(days_from_now: int = 0) -> tuple[str, str]:
    """
    Получить время начала и окончания события.

    Args:
        days_from_now: количество дней от текущей даты.

    Returns:
        Кортеж из startAt и endAt в ISO 8601.
    """
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    start = (now + timedelta(days=days_from_now, hours=1)).replace(
        minute=0,
        second=0,
        microsecond=0,
    )
    end = start + timedelta(minutes=30)

    return start.isoformat(), end.isoformat()


def get_schedule_period(days_back: int = 7, days_forward: int = 30) -> dict:
    """
    Получить период для запроса расписания.

    Args:
        days_back: сколько дней назад включить в период.
        days_forward: сколько дней вперед включить в период.

    Returns:
        Тело запроса для получения расписания.
    """
    tz = timezone(timedelta(hours=3))
    start = datetime.now(tz).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - timedelta(days=days_back)
    end = datetime.now(tz).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=0,
    ) + timedelta(days=days_forward)

    return {
        "from": start.isoformat(),
        "till": end.isoformat(),
        "onlyTypes": [],
    }


def get_required_event_payload(
    title: str | None = None,
    days_from_now: int = 0,
) -> dict:
    """
    Получить тело запроса для создания события.

    Args:
        title: название события.
        days_from_now: количество дней от текущей даты.

    Returns:
        Тело запроса для создания личного события.
    """
    start_at, end_at = get_event_time(days_from_now)

    return {
        "backgroundColor": "#FFF7C7",
        "color": "#FAC641",
        "title": get_event_title() if title is None else title,
        "startAt": start_at,
        "endAt": end_at,
    }


def get_full_event_payload(
    title: str | None = None,
    days_from_now: int = 0,
) -> dict:
    """
    Получить тело запроса для создания события со всеми полями.

    Args:
        title: название события.
        days_from_now: количество дней от текущей даты.

    Returns:
        Тело запроса для создания личного события с описанием.
    """
    payload = get_required_event_payload(title, days_from_now)
    payload["description"] = "Описание автотестового события"

    return payload
