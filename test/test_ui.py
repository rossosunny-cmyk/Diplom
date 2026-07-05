import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from api.personal_events_api import PersonalEventsApi
from config.settings import Settings
from data.event_data import (
    get_event_title,
    get_required_event_payload,
    get_ui_date,
)
from pages.schedule_page import SchedulePage


def open_schedule(driver: WebDriver, settings: Settings) -> SchedulePage:
    """
    Открыть страницу расписания.

    Args:
        driver: экземпляр WebDriver.
        settings: настройки проекта.

    Returns:
        Объект SchedulePage.
    """
    page = SchedulePage(driver, settings.ui_url, settings.timeout)
    page.open_with_token(settings.token)

    return page


def create_event_by_api(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
    title: str,
) -> tuple[int, str]:
    """
    Создать событие через API для предусловия UI-теста.

    Args:
        api_client: API-клиент личных событий.
        event_cleanup: список событий для удаления.
        title: название события.

    Returns:
        Кортеж из id события и startAt.
    """
    payload = get_required_event_payload(title)
    response = api_client.create_personal_event(payload)
    body = response.json()

    event_id = PersonalEventsApi.get_event_id(body)
    start_at = PersonalEventsApi.get_start_at(body, payload["startAt"])
    event_cleanup.append((event_id, start_at))

    return event_id, start_at


def register_ui_event_for_cleanup(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
    title: str,
) -> dict:
    """
    Найти созданное через UI событие и добавить его в очистку.

    Args:
        api_client: API-клиент личных событий.
        event_cleanup: список событий для удаления.
        title: название события.

    Returns:
        Найденное событие.
    """
    event = api_client.find_personal_event_by_title(title)

    assert event is not None

    event_cleanup.append((event["id"], event["startAt"]))

    return event


@allure.title("UI: создание личного события через кнопку плюс")
@allure.story("Smoke: создание через плюс")
@pytest.mark.ui
def test_create_personal_event_via_plus_button(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)

    with allure.step("Создать личное событие через кнопку плюс"):
        title = get_event_title("Smoke создание")
        page.create_personal_event(
            title=title,
            date=get_ui_date(days_from_now=0),
            start_time="09:00",
            end_time="09:30",
        )

    with allure.step("Проверить, что событие появилось в расписании"):
        page.wait_event_title(title)

        assert title in page.get_page_text()

    with allure.step("Добавить созданное событие в очистку"):
        register_ui_event_for_cleanup(api_client, event_cleanup, title)


@allure.title("UI: редактирование существующего личного события")
@allure.story("Smoke: редактирование события")
@pytest.mark.ui
def test_edit_personal_event(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Создать событие через API как предусловие"):
        old_title = get_event_title("Smoke редакт")
        create_event_by_api(api_client, event_cleanup, old_title)

    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)
        page.wait_event_title(old_title)

    with allure.step("Открыть событие и изменить название, описание и цвет"):
        new_title = get_event_title("Изменено")
        page.edit_event(
            old_title=old_title,
            new_title=new_title,
            description="Новое описание события",
            color="yellow",
        )

    with allure.step("Проверить, что событие отображается с новым названием"):
        assert new_title in page.get_page_text()

    with allure.step("Добавить обновленное событие в очистку"):
        register_ui_event_for_cleanup(api_client, event_cleanup, new_title)


@allure.title("UI: удаление существующего личного события")
@allure.story("Smoke: удаление события")
@pytest.mark.ui
def test_delete_personal_event(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Создать событие через API как предусловие"):
        title = get_event_title("Smoke удалить")
        event_id, _ = create_event_by_api(api_client, event_cleanup, title)

    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)
        page.wait_event_title(title)

    with allure.step("Открыть событие и удалить его через UI"):
        page.delete_event(title)

    with allure.step("Проверить, что событие отсутствует в расписании"):
        assert page.is_event_title_visible(title) is False

    with allure.step("Проверить через API, что событие удалено"):
        deleted_event = api_client.find_personal_event_by_title(title)

        assert deleted_event is None or deleted_event["id"] != event_id


@allure.title("UI: создание личного события с выбранным цветом")
@allure.story("Acceptance: выбор цвета события")
@pytest.mark.ui
def test_create_event_with_color_selection(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)

    with allure.step("Создать событие и выбрать зеленый цвет"):
        title = get_event_title("Цвет")
        page.create_personal_event(
            title=title,
            date=get_ui_date(days_from_now=0),
            start_time="10:00",
            end_time="10:30",
            color="green",
        )

    with allure.step("Проверить, что событие сохранено с выбранным цветом"):
        event = register_ui_event_for_cleanup(api_client, event_cleanup, title)

        expected_color = SchedulePage.COLOR_HEX_BY_NAME["green"]

        assert event["title"] == title
        assert str(event["color"]).upper() == expected_color


@allure.title("UI: добавление личного события прошедшей датой")
@allure.story("Acceptance: прошедшая дата")
@pytest.mark.ui
def test_create_event_with_past_date(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)

    with allure.step("Создать событие с прошедшей датой"):
        title = get_event_title("Прошлая дата")
        page.create_personal_event(
            title=title,
            date=get_ui_date(days_from_now=-1),
            start_time="09:00",
            end_time="09:30",
        )

    with allure.step("Проверить через API, что событие сохранено"):
        event = register_ui_event_for_cleanup(api_client, event_cleanup, title)

        assert event["title"] == title


@allure.title("UI: создание события длительностью 25 минут")
@allure.story("Acceptance: минимальная длительность")
@pytest.mark.ui
def test_create_event_with_25_minutes_duration(
    driver: WebDriver,
    settings: Settings,
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Открыть расписание"):
        page = open_schedule(driver, settings)

    with allure.step("Создать событие длительностью 25 минут"):
        title = get_event_title("25 минут")
        page.create_personal_event(
            title=title,
            date=get_ui_date(days_from_now=0),
            start_time="09:00",
            end_time="09:25",
        )

    with allure.step("Проверить через API, что событие сохранено"):
        event = register_ui_event_for_cleanup(api_client, event_cleanup, title)

        assert event["title"] == title
