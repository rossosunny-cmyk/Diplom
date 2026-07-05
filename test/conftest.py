import pytest
from selenium import webdriver

from api.personal_events_api import PersonalEventsApi
from config.settings import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    """
    Получить настройки проекта.

    Returns:
        Объект Settings.
    """
    return get_settings()


@pytest.fixture()
def api_client(settings: Settings) -> PersonalEventsApi:
    """
    Создать API-клиент личных событий.

    Args:
        settings: настройки проекта.

    Returns:
        Клиент PersonalEventsApi.
    """
    return PersonalEventsApi(settings.api_url, settings.token)


@pytest.fixture()
def driver() -> webdriver.Safari:
    """
    Создать WebDriver Safari.

    Returns:
        Экземпляр webdriver.Safari.
    """
    options = webdriver.SafariOptions()
    options.page_load_strategy = "eager"

    browser = webdriver.Safari(options=options)
    browser.set_window_size(1440, 1000)

    yield browser

    browser.quit()


@pytest.fixture()
def event_cleanup(api_client: PersonalEventsApi) -> list[tuple[int, str]]:
    """
    Подготовить список событий для очистки.

    Args:
        api_client: API-клиент личных событий.

    Returns:
        Список пар id и startAt созданных событий.
    """
    events: list[tuple[int, str]] = []

    yield events

    for event_id, start_at in events:
        api_client.remove_personal_event(
            {
                "id": event_id,
                "startAt": start_at,
            }
        )
