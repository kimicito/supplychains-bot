# SupplyChains Bot

Telegram-бот для автоматического ведения канала [@supplychains](https://t.me/supplychains) — игры в логистику, цепочки поставок, обучение.

## Возможности

- 🤖 Полностью автономный режим — публикует посты по расписанию
- 🎮 6 типов контента на неделю
- 📰 Генерация постов с ротацией тем
- 📅 Автопубликация в 09:00 МСК
- 📊 Статистика публикаций

## Расписание

| День | Рубрика | Описание |
|------|---------|----------|
| Пн | 🎮 Game Digest | Новости геймификации и игр в логистику |
| Вт | 🚀 Logistics WOW | Выжимка из supplychains.ru |
| Ср | 📢 Попробуй игру | Анонс игры logistoria.com |
| Чт | 🚀 Logistics WOW | Выжимка из supplychains.ru |
| Пт | 📚 Полка логиста | Книги/фильмы про логистику |
| Сб | 🤫 Тишина | Выходной |
| Вс | 🔥 Итоги недели | Дайджест |

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/kimicito/supplychains-bot.git
cd supplychains-bot

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Отредактировать .env — добавить токены

# Запуск
python3 bot.py
```

## Переменные окружения (.env)

```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
ADMIN_CHAT_ID=your_telegram_chat_id
CHANNEL_ID=@supplychains
```

## Команды бота (для администратора)

| Команда | Описание |
|---------|----------|
| `/start` | Справка |
| `/generate` | Создать пост на сегодня |
| `/post_now` | Опубликовать сразу |
| `/schedule` | Показать расписание |
| `/stats` | Статистика |

## Деплой на сервер

### Вариант 1: Systemd

```bash
sudo cp supplychains-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable supplychains-bot
sudo systemctl start supplychains-bot
```

### Вариант 2: Screen

```bash
screen -dmS supplybot python3 bot.py
```

### Вариант 3: Docker

```bash
docker build -t supplychains-bot .
docker run -d --env-file .env --name supplybot supplychains-bot
```

## Структура

```
supplychains-bot/
├── bot.py              # Главный бот
├── config.py           # Конфигурация и расписание
├── requirements.txt    # Зависимости
├── .env.example        # Шаблон переменных
├── content/
│   ├── published/      # Опубликованные посты
│   └── scheduled/      # Запланированные посты
└── bot_state.json      # Состояние бота
```

## Ресурсы

- **RAM**: ~55 MB
- **Диск**: < 1 MB (без учёта логов)
- **CPU**: минимальная нагрузка

## Лицензия

MIT
