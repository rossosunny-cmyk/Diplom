import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Настройки проекта, полученные из переменных окружения."""

    api_url: str
    ui_url: str
    token: str
    timeout: int


def get_required_env(name: str) -> str:
    """
    Получить обязательную переменную окружения.

    Args:
        name: название переменной окружения.

    Returns:
        Значение переменной окружения.

    Raises:
        RuntimeError: если переменная окружения не задана.
    """
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Set {name} environment variable")

    return value


def get_schedule_url(base_url: str) -> str:
    """
    Получить URL страницы расписания.

    Args:
        base_url: базовый URL кабинета преподавателя.

    Returns:
        URL страницы расписания.
    """
    url = base_url.rstrip("/")

    if url.endswith("/schedule"):
        return url

    return f"{url}/schedule"


def get_settings() -> Settings:
    """
    Получить настройки проекта.

    Returns:
        Объект Settings с базовыми настройками проекта.
    """
    return Settings(
        api_url=get_required_env("SKYENG_API_URL").rstrip("/"),
        ui_url=get_schedule_url(get_required_env("SKYENG_UI_URL")),
        token=get_required_env("SKYENG_TOKEN"),
        timeout=int(os.getenv("SKYENG_TIMEOUT", "20")),
    )
