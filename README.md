# Wildberries Analytics Monitor

Приложение на Python для периодической проверки отчётов Wildberries Analytics API и
отправки изменений в Telegram. Скрипт рассчитан на запуск на Linux/Ubuntu сервере и
подходит для автоматизации через `cron` или `systemd`.

## Возможности

- Получение данных из Wildberries Analytics API.
- Сохранение последнего отчёта на диск и сравнение его с новым.
- Отправка отчётов об изменениях в Telegram.
- Гибкая настройка списка отслеживаемых метрик и интервала опроса.

## Установка

1. Убедитесь, что установлен Python 3.9+ и `pip`.
2. Склонируйте репозиторий и перейдите в каталог проекта.
3. Создайте виртуальное окружение и установите зависимости:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Настройка окружения

Необходимо указать токены и параметры подключения через переменные окружения:

| Переменная            | Описание                                                                 |
|-----------------------|--------------------------------------------------------------------------|
| `WB_API_TOKEN`        | Токен Wildberries Analytics API.                                         |
| `TELEGRAM_BOT_TOKEN`  | Токен Telegram-бота, отправляющего уведомления.                          |
| `TELEGRAM_CHAT_ID`    | ID чата или пользователя для получения сообщений.                        |
| `POLL_INTERVAL_SECONDS` | (опционально) Интервал между запросами в секундах. По умолчанию 3600. |
| `WB_ANALYTICS_URL`    | (опционально) Пользовательский URL для API.                              |
| `STATE_FILE`          | (опционально) Путь к файлу с последним отчётом.                          |
| `TRACKED_METRICS`     | (опционально) CSV список метрик для отслеживания.                        |
| `TRACKED_KEY_FIELD`   | (опционально) Название поля, идентифицирующего товар.                    |

Пример `.env` файла:

```bash
WB_API_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=123456789:ABCDEF...
TELEGRAM_CHAT_ID=123456789
POLL_INTERVAL_SECONDS=3600
```

Подгрузить переменные можно через `export $(cat .env | xargs)` или средствами
используемой системы конфигурации.

## Запуск

Для разового запуска (например, при тестировании):

```bash
python -m wb_monitor.main --run-once --log-level debug
```

Для постоянной работы оставьте процесс в цикле:

```bash
python -m wb_monitor.main
```

### Настройка cron

Пример задания cron, выполняющего проверку каждый час:

```cron
0 * * * * /usr/bin/env bash -lc 'cd /path/to/project && source .venv/bin/activate && python -m wb_monitor.main --run-once'
```

### Настройка systemd

Создайте юнит `/etc/systemd/system/wb-monitor.service`:

```ini
[Unit]
Description=Wildberries Analytics Monitor
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/project
EnvironmentFile=/path/to/project/.env
ExecStart=/path/to/project/.venv/bin/python -m wb_monitor.main
Restart=always

[Install]
WantedBy=multi-user.target
```

После чего выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wb-monitor.service
```

## Кастомизация сообщений

Можно указать файл с отображаемыми названиями метрик, передав его через
`--metrics-aliases`. Файл должен содержать JSON объект, где ключ — имя метрики, а
значение — отображаемое название.

Пример `metrics.json`:

```json
{
  "ordersCount": "Количество заказов",
  "revenue": "Выручка"
}
```

Запустите монитор со своим файлом:

```bash
python -m wb_monitor.main --metrics-aliases metrics.json
```

## Зависимости

Список зависимостей находится в `requirements.txt`. При обновлении библиотек не забудьте
перезапустить сервис.

