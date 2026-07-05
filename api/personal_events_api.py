import requests

from data.event_data import get_schedule_period


class PersonalEventsApi:
    """Клиент API личных событий Skyeng."""

    def __init__(self, base_url: str, token: str) -> None:
        """
        Создать API-клиент.

        Args:
            base_url: базовый URL API.
            token: значение cookie token_global.

        Returns:
            None.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Cookie": f"token_global={token}",
        }

    def get_schedule(self, payload: dict) -> requests.Response:
        """
        Получить расписание за период.

        Args:
            payload: тело запроса с периодом расписания.

        Returns:
            Ответ requests.Response.
        """
        return requests.post(
            f"{self.base_url}/v2/schedule/events",
            json=payload,
            headers=self.headers,
        )

    def create_personal_event(self, payload: dict) -> requests.Response:
        """
        Создать личное событие.

        Args:
            payload: тело запроса для создания события.

        Returns:
            Ответ requests.Response.
        """
        return requests.post(
            f"{self.base_url}/v2/schedule/createPersonal",
            json=payload,
            headers=self.headers,
        )

    def update_personal_event(self, payload: dict) -> requests.Response:
        """
        Обновить личное событие.

        Args:
            payload: тело запроса для обновления события.

        Returns:
            Ответ requests.Response.
        """
        return requests.post(
            f"{self.base_url}/v2/schedule/updatePersonal",
            json=payload,
            headers=self.headers,
        )

    def remove_personal_event(self, payload: dict) -> requests.Response:
        """
        Удалить личное событие.

        Args:
            payload: тело запроса для удаления события.

        Returns:
            Ответ requests.Response.
        """
        return requests.post(
            f"{self.base_url}/v2/schedule/removePersonal",
            json=payload,
            headers=self.headers,
        )

    def find_personal_event_by_title(self, title: str) -> dict | None:
        """
        Найти личное событие в расписании по названию.

        Args:
            title: название личного события.

        Returns:
            Словарь с данными события или None, если событие не найдено.
        """
        response = self.get_schedule(get_schedule_period())
        body = response.json()
        data = body.get("data") or {}
        events = data.get("events") or []

        for event in events:
            raw_payload = event.get("payload") or {}
            event_payload = self._get_schedule_event_payload(event)

            if event_payload.get("title") != title:
                continue

            event_id = (
                event_payload.get("id")
                or raw_payload.get("id")
                or event.get("id")
            )
            start_at = (
                event.get("startAt")
                or raw_payload.get("startAt")
                or event_payload.get("startAt")
                or event.get("start")
            )

            if event_id is None or start_at is None:
                return None

            return {
                "id": int(event_id),
                "startAt": str(start_at),
                "title": str(event_payload["title"]),
                "color": event_payload.get("color"),
                "backgroundColor": event_payload.get("backgroundColor"),
                "durationSeconds": event.get("durationSeconds"),
            }

        return None

    @staticmethod
    def _get_schedule_event_payload(event: dict) -> dict:
        """
        Получить payload события из ответа расписания.

        Args:
            event: событие из ответа /v2/schedule/events.

        Returns:
            Payload личного события.
        """
        payload = event.get("payload") or {}

        if isinstance(payload.get("payload"), dict):
            return payload["payload"]

        return payload

    @staticmethod
    def get_event_id(response_body: dict) -> int:
        """
        Получить id события из ответа API.

        Args:
            response_body: тело ответа API.

        Returns:
            Идентификатор события.
        """
        data = response_body.get("data") or {}

        if "payload" in data and data["payload"] is not None:
            return int(data["payload"]["id"])

        return int(data["id"])

    @staticmethod
    def get_start_at(response_body: dict, fallback: str) -> str:
        """
        Получить startAt события из ответа API.

        Args:
            response_body: тело ответа API.
            fallback: запасное значение startAt.

        Returns:
            Значение startAt.
        """
        data = response_body.get("data") or {}

        if "startAt" in data and data["startAt"] is not None:
            return str(data["startAt"])

        if "payload" in data and data["payload"] is not None:
            payload = data["payload"]

            if "startAt" in payload and payload["startAt"] is not None:
                return str(payload["startAt"])

        return fallback

    @staticmethod
    def get_errors(response_body: dict) -> list:
        """
        Получить список ошибок из ответа API.

        Args:
            response_body: тело ответа API.

        Returns:
            Список ошибок.
        """
        return response_body.get("errors") or []

    @staticmethod
    def has_error_code(response_body: dict, error_code: str) -> bool:
        """
        Проверить наличие ошибки с указанным кодом.

        Args:
            response_body: тело ответа API.
            error_code: ожидаемый код ошибки.

        Returns:
            True, если ошибка найдена, иначе False.
        """
        errors = PersonalEventsApi.get_errors(response_body)

        for item in errors:
            error = item.get("error") or {}

            if error.get("code") == error_code:
                return True

        return False

    @staticmethod
    def has_error_property(response_body: dict, property_name: str) -> bool:
        """
        Проверить наличие ошибки по указанному полю.

        Args:
            response_body: тело ответа API.
            property_name: название поля.

        Returns:
            True, если ошибка по полю найдена, иначе False.
        """
        errors = PersonalEventsApi.get_errors(response_body)

        return any(item.get("property") == property_name for item in errors)

    @staticmethod
    def has_error_message(response_body: dict, message: str) -> bool:
        """
        Проверить наличие текста ошибки в ответе.

        Args:
            response_body: тело ответа API.
            message: ожидаемый текст ошибки.

        Returns:
            True, если текст ошибки найден, иначе False.
        """
        return message in str(response_body)
