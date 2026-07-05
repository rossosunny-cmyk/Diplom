import allure
import pytest

from api.personal_events_api import PersonalEventsApi
from data.event_data import (
    get_full_event_payload,
    get_max_length_title,
    get_required_event_payload,
    get_schedule_period,
    get_too_long_title,
)


def register_event_for_cleanup(
    response_body: dict,
    payload: dict,
    event_cleanup: list[tuple[int, str]],
) -> tuple[int, str]:
    """
    Сохранить событие для последующей очистки.

    Args:
        response_body: тело ответа API.
        payload: тело запроса создания события.
        event_cleanup: список событий для удаления.

    Returns:
        Кортеж из id события и startAt.
    """
    event_id = PersonalEventsApi.get_event_id(response_body)
    start_at = PersonalEventsApi.get_start_at(
        response_body,
        payload["startAt"],
    )
    event_cleanup.append((event_id, start_at))

    return event_id, start_at


@allure.title("API: получение расписания за период")
@allure.story("Расписание: получение списка событий")
@pytest.mark.api
def test_get_schedule(api_client: PersonalEventsApi) -> None:
    with allure.step("Подготовить период для получения расписания"):
        payload = get_schedule_period()

    with allure.step("Отправить запрос POST /v2/schedule/events"):
        response = api_client.get_schedule(payload)
        body = response.json()

    with allure.step("Проверить успешный ответ"):
        assert response.status_code == 200
        assert "data" in body
        assert PersonalEventsApi.get_errors(body) == []


@allure.title("API: создание события с обязательными полями")
@allure.story("Создание: обязательные поля")
@pytest.mark.api
def test_create_event_with_required_fields(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Подготовить тело запроса с обязательными полями"):
        payload = get_required_event_payload()

    with allure.step("Создать личное событие"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Сохранить событие для очистки"):
        event_id, _ = register_event_for_cleanup(body, payload, event_cleanup)

    with allure.step("Проверить созданное событие"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert event_id > 0


@allure.title("API: создание события с описанием")
@allure.story("Создание: все поля")
@pytest.mark.api
def test_create_event_with_all_fields(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Подготовить тело запроса со всеми полями"):
        payload = get_full_event_payload()

    with allure.step("Создать личное событие"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Сохранить событие для очистки"):
        event_id, _ = register_event_for_cleanup(body, payload, event_cleanup)

    with allure.step("Проверить созданное событие"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert event_id > 0


@allure.title("API: создание события с названием длиной 1 символ")
@allure.story("Создание: минимальная длина title")
@pytest.mark.api
def test_create_event_with_min_title_length(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Подготовить тело запроса с названием из 1 символа"):
        payload = get_required_event_payload("А")

    with allure.step("Создать личное событие"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Сохранить событие для очистки"):
        event_id, _ = register_event_for_cleanup(body, payload, event_cleanup)

    with allure.step("Проверить созданное событие"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert event_id > 0


@allure.title("API: создание события с названием длиной 40 символов")
@allure.story("Создание: максимальная длина title")
@pytest.mark.api
def test_create_event_with_max_title_length(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Подготовить тело запроса с названием из 40 символов"):
        payload = get_required_event_payload(get_max_length_title())

    with allure.step("Создать личное событие"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Сохранить событие для очистки"):
        event_id, _ = register_event_for_cleanup(body, payload, event_cleanup)

    with allure.step("Проверить созданное событие"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert event_id > 0


@allure.title("API: изменение названия события")
@allure.story("Обновление: изменение title")
@pytest.mark.api
def test_update_event_title(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Создать событие для обновления"):
        payload = get_required_event_payload()
        create_response = api_client.create_personal_event(payload)
        create_body = create_response.json()
        event_id, start_at = register_event_for_cleanup(
            create_body,
            payload,
            event_cleanup,
        )

    with allure.step("Отправить запрос на изменение названия"):
        new_title = "Обновленное событие"
        update_payload = {
            **payload,
            "id": event_id,
            "oldStartAt": start_at,
            "startAt": start_at,
            "title": new_title,
        }
        response = api_client.update_personal_event(update_payload)
        body = response.json()

    with allure.step("Проверить успешное обновление"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert PersonalEventsApi.get_event_id(body) > 0


@allure.title("API: обновление цвета события")
@allure.story("Обновление: изменение цвета")
@pytest.mark.api
def test_update_event_color(
    api_client: PersonalEventsApi,
    event_cleanup: list[tuple[int, str]],
) -> None:
    with allure.step("Создать событие для обновления"):
        payload = get_required_event_payload()
        create_response = api_client.create_personal_event(payload)
        create_body = create_response.json()
        event_id, start_at = register_event_for_cleanup(
            create_body,
            payload,
            event_cleanup,
        )

    with allure.step("Отправить запрос на обновление цвета"):
        update_payload = {
            **payload,
            "id": event_id,
            "oldStartAt": start_at,
            "startAt": start_at,
            "backgroundColor": "#FFEBEE",
            "color": "#C62828",
        }
        response = api_client.update_personal_event(update_payload)
        body = response.json()

    with allure.step("Проверить успешное обновление"):
        assert response.status_code == 200
        assert PersonalEventsApi.get_errors(body) == []
        assert PersonalEventsApi.get_event_id(body) > 0


@allure.title("API: удаление созданного события")
@allure.story("Удаление: успешное удаление")
@pytest.mark.api
def test_delete_event(api_client: PersonalEventsApi) -> None:
    with allure.step("Создать событие для удаления"):
        payload = get_required_event_payload()
        create_response = api_client.create_personal_event(payload)
        create_body = create_response.json()
        event_id = PersonalEventsApi.get_event_id(create_body)
        start_at = PersonalEventsApi.get_start_at(
            create_body,
            payload["startAt"],
        )

    with allure.step("Удалить созданное событие"):
        remove_response = api_client.remove_personal_event(
            {
                "id": event_id,
                "startAt": start_at,
            }
        )
        remove_body = remove_response.json()

    with allure.step("Проверить успешное удаление"):
        assert remove_response.status_code == 200
        assert PersonalEventsApi.get_errors(remove_body) == []


@allure.title("API: создание события с пустым названием")
@allure.story("Валидация: пустой title")
@pytest.mark.api
def test_create_event_with_empty_title(api_client: PersonalEventsApi) -> None:
    with allure.step("Подготовить тело запроса с пустым title"):
        payload = get_required_event_payload("")
        payload["title"] = ""

    with allure.step("Отправить запрос создания события"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Проверить ошибку валидации"):
        assert response.status_code == 200
        assert PersonalEventsApi.has_error_code(body, "not_valid")


@allure.title("API: создание события с названием больше 40 символов")
@allure.story("Валидация: превышение длины title")
@pytest.mark.api
def test_create_event_with_too_long_title(
    api_client: PersonalEventsApi,
) -> None:
    with allure.step("Подготовить тело запроса с title длиной 41 символ"):
        payload = get_required_event_payload(get_too_long_title())

    with allure.step("Отправить запрос создания события"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Проверить ошибку валидации по title"):
        assert response.status_code == 200
        assert PersonalEventsApi.has_error_property(body, "title")
        assert PersonalEventsApi.has_error_code(body, "not_valid")


@allure.title("API: создание события с невалидным цветом")
@allure.story("Валидация: некорректный color")
@pytest.mark.api
def test_create_event_with_invalid_color(
    api_client: PersonalEventsApi,
) -> None:
    with allure.step("Подготовить тело запроса с невалидным color"):
        payload = get_required_event_payload()
        payload["color"] = "#ZXZX"

    with allure.step("Отправить запрос создания события"):
        response = api_client.create_personal_event(payload)
        body = response.json()

    with allure.step("Проверить ошибку валидации по color"):
        assert response.status_code == 200
        assert PersonalEventsApi.has_error_property(body, "color")
        assert PersonalEventsApi.has_error_code(body, "not_valid")


@allure.title("API: обновление события с несуществующим id")
@allure.story("Бизнес-ошибка: updatePersonal")
@pytest.mark.api
def test_update_event_with_not_existing_id(
    api_client: PersonalEventsApi,
) -> None:
    with allure.step("Подготовить тело запроса с несуществующим id"):
        payload = get_required_event_payload("Обновленное название")
        payload["id"] = 777
        payload["oldStartAt"] = payload["startAt"]

    with allure.step("Отправить запрос обновления события"):
        response = api_client.update_personal_event(payload)
        body = response.json()

    with allure.step("Проверить ошибку domain_error"):
        assert response.status_code == 200
        assert PersonalEventsApi.has_error_code(body, "domain_error")
        assert PersonalEventsApi.has_error_message(
            body,
            "Personal event not found",
        )


@allure.title("API: удаление события с несуществующим id")
@allure.story("Бизнес-ошибка: removePersonal")
@pytest.mark.api
def test_delete_event_with_not_existing_id(
    api_client: PersonalEventsApi,
) -> None:
    with allure.step("Подготовить тело запроса с несуществующим id"):
        payload = {
            "id": 777,
            "startAt": get_required_event_payload()["startAt"],
        }

    with allure.step("Отправить запрос удаления события"):
        response = api_client.remove_personal_event(payload)
        body = response.json()

    with allure.step("Проверить ошибку domain_error"):
        assert response.status_code == 200
        assert PersonalEventsApi.has_error_code(body, "domain_error")
        assert PersonalEventsApi.has_error_message(
            body,
            "Personal event not found",
        )
