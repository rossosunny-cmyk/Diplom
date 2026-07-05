from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class SchedulePage:
    """Page Object страницы расписания Skyeng."""

    CREATE_BUTTON = (
        By.XPATH,
        "//button[.//div[contains(@class, 'content') "
        "and normalize-space()='Создать']]",
    )
    DIALOG = (By.CSS_SELECTOR, "tc-dialog-view")
    PERSONAL_EVENT_TAB = (
        By.XPATH,
        "//input[@name='slotEditType' and @value='personal-event']"
        "/ancestor::label",
    )
    PERSONAL_EVENT_FORM = (
        By.CSS_SELECTOR,
        "app-schedule-personal-event-form",
    )
    TITLE_INPUT = (
        By.XPATH,
        "//app-schedule-personal-event-form"
        "//input[@maxlength='40' and contains(@placeholder, 'вебинар')]",
    )
    START_DATE_SELECT = (
        By.XPATH,
        "(//app-schedule-personal-event-form"
        "//app-date-time-select//select[not(@disabled)])[1]",
    )
    START_TIME_INPUT = (
        By.XPATH,
        "(//app-schedule-personal-event-form"
        "//teachers-time-picker//input)[1]",
    )
    END_TIME_INPUT = (
        By.XPATH,
        "(//app-schedule-personal-event-form"
        "//teachers-time-picker//input)[2]",
    )
    DESCRIPTION_TEXTAREA = (
        By.XPATH,
        "//app-schedule-personal-event-form"
        "//textarea[contains(@placeholder, 'ссылка')]",
    )
    SAVE_BUTTON = (
        By.XPATH,
        "//tc-dialog-view//footer//button"
        "[.//div[contains(@class, 'content') "
        "and normalize-space()='Сохранить'] "
        "and not(contains(@class, '-disabled'))]",
    )

    COLOR_HEX_BY_NAME = {
        "gray": "#81888D",
        "yellow": "#FAC641",
        "green": "#43B658",
        "purple": "#D478F1",
    }

    SCROLL_CENTER_SCRIPT = (
        "arguments[0].scrollIntoView("
        "{block: 'center', inline: 'center'}"
        ");"
    )

    def __init__(self, driver: WebDriver, url: str, timeout: int) -> None:
        """
        Создать объект страницы расписания.

        Args:
            driver: экземпляр WebDriver.
            url: URL страницы расписания.
            timeout: время ожидания элементов.

        Returns:
            None.
        """
        self.driver = driver
        self.url = url
        self.wait = WebDriverWait(driver, min(timeout, 15))
        self.short_wait = WebDriverWait(driver, 3)

    def open_with_token(self, token: str) -> None:
        """
        Открыть страницу расписания с авторизацией через cookie.

        Args:
            token: значение cookie token_global.

        Returns:
            None.
        """
        self.driver.get("https://id.skyeng.ru")
        self.driver.add_cookie(
            {
                "name": "token_global",
                "value": token,
                "domain": ".skyeng.ru",
                "path": "/",
                "secure": True,
            }
        )
        self.driver.get(self.url)
        self.wait_until_opened()

    def wait_until_opened(self) -> None:
        """
        Дождаться открытия страницы расписания.

        Returns:
            None.
        """
        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body")),
            "Страница расписания не открылась",
        )

        if "id.skyeng.ru/login" in self.driver.current_url:
            raise AssertionError(
                "Открылась страница логина, cookie не сработала"
            )

    def get_page_text(self) -> str:
        """
        Получить текст страницы.

        Returns:
            Текст страницы.
        """
        return self.driver.find_element(By.TAG_NAME, "body").text

    def click_create_button(self) -> None:
        """
        Нажать кнопку Создать.

        Returns:
            None.
        """
        button = self.wait.until(
            EC.presence_of_element_located(self.CREATE_BUTTON),
            "Кнопка Создать не найдена",
        )
        self._js_click(button)
        self.wait.until(
            EC.visibility_of_element_located(self.DIALOG),
            "Окно создания события не открылось",
        )

    def select_personal_event_tab(self) -> None:
        """
        Выбрать вкладку Личное событие.

        Returns:
            None.
        """
        tab = self.wait.until(
            EC.presence_of_element_located(self.PERSONAL_EVENT_TAB),
            "Вкладка Личное событие не найдена",
        )
        self._js_click(tab)
        self.wait.until(
            EC.visibility_of_element_located(self.PERSONAL_EVENT_FORM),
            "Форма личного события не открылась",
        )

    def create_personal_event(
        self,
        title: str,
        description: str | None = None,
        date: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        color: str | None = None,
    ) -> None:
        """
        Создать личное событие через UI.

        Args:
            title: название события.
            description: описание события.
            date: дата в формате ДД.ММ.ГГГГ.
            start_time: время начала.
            end_time: время окончания.
            color: цвет события.

        Returns:
            None.
        """
        self.click_create_button()
        self.select_personal_event_tab()
        self.fill_title(title)

        if date is not None:
            self.select_start_date(date)

        if start_time is not None:
            self.fill_start_time(start_time)

        if end_time is not None:
            self.fill_end_time(end_time)

        if description is not None:
            self.fill_description(description)

        if color is not None:
            self.select_color(color)

        self.submit_event_form()
        self.wait_event_title(title)

    def fill_title(self, title: str) -> None:
        """
        Заполнить название события.

        Args:
            title: название события.

        Returns:
            None.
        """
        field = self.wait.until(
            EC.visibility_of_element_located(self.TITLE_INPUT),
            "Поле Название события не найдено",
        )
        self._set_value(field, title)

    def select_start_date(self, date: str) -> None:
        """
        Выбрать дату начала события.

        Args:
            date: дата в формате ДД.ММ.ГГГГ.

        Returns:
            None.
        """
        date_label = self._format_ui_date(date)
        select_element = self.wait.until(
            EC.presence_of_element_located(self.START_DATE_SELECT),
            "Список дат начала события не найден",
        )
        select = Select(select_element)

        for option in select.options:
            if option.text.strip() == date_label:
                select.select_by_visible_text(option.text)
                return

        raise AssertionError(f"Дата не найдена в списке: {date_label}")

    def fill_start_time(self, start_time: str) -> None:
        """
        Заполнить время начала события.

        Args:
            start_time: время начала.

        Returns:
            None.
        """
        field = self.wait.until(
            EC.visibility_of_element_located(self.START_TIME_INPUT),
            "Поле времени начала не найдено",
        )
        self._set_value(field, start_time)

    def fill_end_time(self, end_time: str) -> None:
        """
        Заполнить время окончания события.

        Args:
            end_time: время окончания.

        Returns:
            None.
        """
        field = self.wait.until(
            EC.visibility_of_element_located(self.END_TIME_INPUT),
            "Поле времени окончания не найдено",
        )
        self._set_value(field, end_time)

    def fill_description(self, description: str) -> None:
        """
        Заполнить описание события.

        Args:
            description: описание события.

        Returns:
            None.
        """
        field = self.wait.until(
            EC.visibility_of_element_located(self.DESCRIPTION_TEXTAREA),
            "Поле Описание не найдено",
        )
        self._set_value(field, description)

    def select_color(self, color: str) -> None:
        """
        Выбрать цвет события.

        Args:
            color: название цвета: gray, yellow, green или purple.

        Returns:
            None.
        """
        color_hex = self.COLOR_HEX_BY_NAME.get(color)

        if color_hex is None:
            raise AssertionError(f"Цвет не поддерживается формой: {color}")

        color_picker = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "app-schedule-personal-event-form app-color-picker",
                )
            ),
            "Блок выбора цвета не найден",
        )
        self.driver.execute_script(
            self.SCROLL_CENTER_SCRIPT,
            color_picker,
        )

        locator = (
            By.XPATH,
            "//app-schedule-personal-event-form//app-color-picker"
            "//div[contains(@class, 'color-circle')]"
            "[.//*[local-name()='path' "
            "and translate(@fill, 'abcdef', 'ABCDEF')="
            f"{self._xpath_literal(color_hex)}]]",
        )
        element = self.wait.until(
            EC.presence_of_element_located(locator),
            f"Цвет не найден в палитре: {color}",
        )
        self._native_click(element)

    def submit_event_form(self) -> None:
        """
        Сохранить форму создания или редактирования события.

        Returns:
            None.
        """
        button = self.wait.until(
            EC.presence_of_element_located(self.SAVE_BUTTON),
            "Кнопка Сохранить не найдена или неактивна",
        )
        self._native_click(button)
        self.wait.until_not(
            EC.visibility_of_element_located(self.PERSONAL_EVENT_FORM),
            "Форма события не закрылась после сохранения",
        )

    def wait_event_title(self, title: str) -> None:
        """
        Дождаться появления события в расписании.

        Args:
            title: название события.

        Returns:
            None.
        """
        self.wait.until(
            EC.presence_of_element_located(
                self._calendar_event_locator(title)
            ),
            f"Событие не найдено в расписании: {title}",
        )

    def wait_event_disappeared(self, title: str) -> None:
        """
        Дождаться исчезновения события из календаря.

        Args:
            title: название события.

        Returns:
            None.
        """
        self.wait.until(
            lambda driver: len(
                driver.find_elements(*self._calendar_event_locator(title))
            )
            == 0,
            f"Событие не исчезло из расписания: {title}",
        )

    def is_event_title_visible(self, title: str) -> bool:
        """
        Проверить, видно ли событие в расписании.

        Args:
            title: название события.

        Returns:
            True, если событие видно, иначе False.
        """
        elements = self.driver.find_elements(
            *self._calendar_event_locator(title)
        )

        return any(element.is_displayed() for element in elements)

    def open_event(self, title: str) -> None:
        """
        Открыть событие в расписании.

        Args:
            title: название события.

        Returns:
            None.
        """
        self.wait_event_title(title)

        event = self.wait.until(
            EC.presence_of_element_located(
                self._calendar_event_locator(title)
            ),
            f"Карточка события не найдена в календаре: {title}",
        )
        self._native_click(event)

        self.wait.until(
            EC.visibility_of_element_located(self.DIALOG),
            f"Окно события не открылось: {title}",
        )
        self.wait.until(
            EC.text_to_be_present_in_element(self.DIALOG, title),
            f"Открылось окно не того события: {title}",
        )

    def delete_event(self, title: str) -> None:
        """
        Удалить событие через UI.

        Args:
            title: название события.

        Returns:
            None.
        """
        self.open_event(title)
        self._click_first_button_by_text(
            [
                "Удалить",
                "Удалить событие",
            ]
        )
        self._confirm_delete_if_needed()
        self.wait_event_disappeared(title)

    def edit_event(
        self,
        old_title: str,
        new_title: str,
        description: str | None = None,
        date: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        color: str | None = None,
    ) -> None:
        """
        Отредактировать событие через UI.

        Args:
            old_title: старое название события.
            new_title: новое название события.
            description: новое описание.
            date: новая дата.
            start_time: новое время начала.
            end_time: новое время окончания.
            color: новый цвет.

        Returns:
            None.
        """
        self.open_event(old_title)
        self._click_first_button_by_text(
            [
                "Редактировать",
                "Изменить",
                "Настроить",
            ]
        )
        self._confirm_edit_scope_if_needed()
        self.wait.until(
            EC.visibility_of_element_located(self.PERSONAL_EVENT_FORM),
            "Форма редактирования личного события не открылась",
        )

        self.fill_title(new_title)

        if date is not None:
            self.select_start_date(date)

        if start_time is not None:
            self.fill_start_time(start_time)

        if end_time is not None:
            self.fill_end_time(end_time)

        if description is not None:
            self.fill_description(description)

        if color is not None:
            self.select_color(color)

        self.submit_event_form()
        self.wait_event_title(new_title)

    def _click_first_button_by_text(self, texts: list[str]) -> None:
        """
        Нажать первую найденную кнопку из списка текстов.

        Args:
            texts: варианты текста кнопки.

        Returns:
            None.
        """
        last_error = None

        for text in texts:
            try:
                self._click_button_by_text(text)
                return
            except TimeoutException as error:
                last_error = error

        if last_error is not None:
            raise last_error

    def _click_button_by_text(self, text: str) -> None:
        """
        Нажать кнопку в окне события по тексту.

        Args:
            text: текст кнопки.

        Returns:
            None.
        """
        literal = self._xpath_literal(text)
        locator = (
            By.XPATH,
            "//tc-dialog-view//footer//button"
            "[.//div[contains(@class, 'content') "
            f"and normalize-space()={literal}]]",
        )
        button = self.wait.until(
            EC.presence_of_element_located(locator),
            f"Кнопка не найдена в окне события: {text}",
        )
        self._native_click(button)

    def _confirm_edit_scope_if_needed(self) -> None:
        """
        Подтвердить область редактирования события, если появилось окно выбора.

        Returns:
            None.
        """
        scope_label_locator = (
            By.XPATH,
            "//tc-dialog-view//input"
            "[@name='personalEventScope' and @value='occurrence']"
            "/ancestor::label",
        )
        confirm_button_locator = (
            By.XPATH,
            "//tc-dialog-view//footer//button"
            "[.//div[contains(@class, 'content') "
            "and normalize-space()='Подтвердить']]",
        )

        try:
            scope_label = self.short_wait.until(
                EC.presence_of_element_located(scope_label_locator)
            )
        except TimeoutException:
            return

        self._native_click(scope_label)

        confirm_button = self.wait.until(
            EC.presence_of_element_located(confirm_button_locator),
            "Кнопка Подтвердить не найдена в окне выбора области",
        )
        self._native_click(confirm_button)

    def _confirm_delete_if_needed(self) -> None:
        """
        Подтвердить удаление, если появилось окно подтверждения.

        Returns:
            None.
        """
        for text in ["Да, удалить", "Удалить", "Подтвердить"]:
            literal = self._xpath_literal(text)
            locator = (
                By.XPATH,
                "//tc-dialog-view//footer//button"
                "[.//div[contains(@class, 'content') "
                f"and normalize-space()={literal}]]",
            )

            try:
                button = self.short_wait.until(
                    EC.presence_of_element_located(locator)
                )
                self._native_click(button)
                return
            except TimeoutException:
                continue

    def _set_value(self, field: WebElement, value: str) -> None:
        """
        Установить значение в поле.

        Args:
            field: поле ввода.
            value: новое значение.

        Returns:
            None.
        """
        self._js_click(field)
        field.send_keys(Keys.COMMAND, "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(value)
        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            field,
        )

    def _calendar_event_locator(self, title: str) -> tuple[str, str]:
        """
        Получить точный локатор личного события в календаре.

        Args:
            title: название события.

        Returns:
            Selenium locator.
        """
        literal = self._xpath_literal(title)

        return (
            By.XPATH,
            "//tcc-calendar-event-personal"
            "[.//div[contains(@class, 'long-view__title') "
            f"and normalize-space()={literal}] "
            "or .//span[contains(@class, 'short-view__title') "
            f"and normalize-space()={literal}] "
            f"or .//*[contains(normalize-space(), {literal})]]",
        )

    def _native_click(self, element: WebElement) -> None:
        """
        Кликнуть по элементу нативным кликом Safari.

        Args:
            element: элемент страницы.

        Returns:
            None.
        """
        self.driver.execute_script(
            self.SCROLL_CENTER_SCRIPT,
            element,
        )

        try:
            element.click()
            return
        except WebDriverException:
            self.driver.execute_script(
                """
                const element = arguments[0];

                const eventNames = [
                    'mouseover',
                    'mousedown',
                    'mouseup',
                    'click'
                ];

                for (const name of eventNames) {
                    element.dispatchEvent(
                        new MouseEvent(
                            name,
                            {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }
                        )
                    );
                }
                """,
                element,
            )

    def _js_click(self, element: WebElement) -> None:
        """
        Кликнуть по элементу через JavaScript.

        Args:
            element: элемент страницы.

        Returns:
            None.
        """
        self.driver.execute_script(
            self.SCROLL_CENTER_SCRIPT,
            element,
        )
        self.driver.execute_script("arguments[0].click();", element)

    @staticmethod
    def _format_ui_date(date: str) -> str:
        """
        Преобразовать дату из ДД.ММ.ГГГГ в формат интерфейса.

        Args:
            date: дата в формате ДД.ММ.ГГГГ.

        Returns:
            Дата в формате интерфейса, например Сб, 4 июля.
        """
        date_value = datetime.strptime(date, "%d.%m.%Y")
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        months = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря",
        }

        return (
            f"{weekdays[date_value.weekday()]}, "
            f"{date_value.day} {months[date_value.month]}"
        )

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """
        Подготовить строку для XPath.

        Args:
            value: исходное значение.

        Returns:
            XPath literal.
        """
        if "'" not in value:
            return f"'{value}'"

        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        xpath_parts = []

        for index, part in enumerate(parts):
            if part:
                xpath_parts.append(f"'{part}'")

            if index != len(parts) - 1:
                xpath_parts.append('"\'"')

        return "concat(" + ", ".join(xpath_parts) + ")"
