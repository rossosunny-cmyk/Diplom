# Skyeng Personal Events Autotests

Проект содержит UI- и API-автотесты для функциональности **«Личные события»** в разделе **«Расписание»** онлайн-школы Skyeng.

Ссылка на финальный проект по ручному тестированию: https://lomakinaas.yonote.ru/share/4919e753-c5bb-4034-90f7-4b132776ef3d

Автотесты подготовлены по результатам финальной работы по ручному тестированию и API-курсовой работы.

## Структура проекта

```text
skyeng_personal_events_autotests/
├── api/
│   └── personal_events_api.py
├── config/
│   └── settings.py
├── data/
│   └── event_data.py
├── pages/
│   └── schedule_page.py
├── test/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_ui.py
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

## Подготовка

Установить зависимости:

```bash
pip install -r requirements.txt
```

Перед запуском нужно указать переменные окружения:

```text
SKYENG_API_URL=<базовый URL API>
SKYENG_UI_URL=<URL кабинета преподавателя>
SKYENG_TOKEN=<значение cookie token_global>
```

В коде нет логинов, паролей, токенов и других чувствительных данных.

## Запуск тестов

Запустить все тесты:

```bash
pytest
```

Запустить только UI-тесты:

```bash
pytest -m "ui"
```

Запустить только API-тесты:

```bash
pytest -m "api"
```

## Запуск тестов с генерацией Allure-результатов

Перед новым запуском можно удалить старые результаты:

```bash
rm -rf allure-results allure-report
```

Запустить все тесты с сохранением Allure-результатов:

```bash
pytest --alluredir=allure-results
```

Запустить только UI-тесты с сохранением Allure-результатов:

```bash
pytest -m "ui" --alluredir=allure-results
```

Запустить только API-тесты с сохранением Allure-результатов:

```bash
pytest -m "api" --alluredir=allure-results
```

Открыть Allure-отчет:

```bash
allure serve allure-results
```

Сформировать статический Allure-отчет:

```bash
allure generate allure-results -o allure-report --clean
```

## Примечания

UI-тесты покрывают smoke- и приемочные сценарии: создание через кнопку плюс, редактирование, удаление, выбор цвета, прошедшую дату и длительность 25 минут.

API-тесты покрывают получение расписания, создание, обновление, удаление и проверки бизнес-ошибок.
