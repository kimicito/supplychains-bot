"""Конфигурация бота под канал @supplychains — полностью автономный режим."""

import os
from pathlib import Path

# === Telegram ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "143946238")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@supplychains")

# === Источники ===
SUPPLYCHAINS_URL = "https://supplychains.ru"
LOGISTORIA_URL = "https://logistoria.com"

# === Исключённые регионы (для новостей) ===
EXCLUDED_COUNTRIES = ["Украина", "Ukraine", "Польша", "Poland", "украина", "польша"]

# === База статей supplychains.ru/blog ===
# Ротация: 19 статей, не повторяем ~3 месяца
# Чтение в день публикации (вт/чт в 11:00 МСК)

ARTICLES_DATABASE = [
    {"slug": "logistika-domashnih-hozyaistv", "url": "https://supplychains.ru/blog/logistika-domashnih-hozyaistv"},
    {"slug": "logistika-obshestvennogo-pitaniya", "url": "https://supplychains.ru/blog/logistika-obshestvennogo-pitaniya"},
    {"slug": "upravlenie-zapasami", "url": "https://supplychains.ru/blog/upravlenie-zapasami"},
    {"slug": "logistika-tovarnogo-sklada", "url": "https://supplychains.ru/blog/logistika-tovarnogo-sklada"},
    {"slug": "logistika-optovoy-torgovli", "url": "https://supplychains.ru/blog/logistika-optovoy-torgovli"},
    {"slug": "logistika-transportnoy-kompanii", "url": "https://supplychains.ru/blog/logistika-transportnoy-kompanii"},
    {"slug": "model-pyati-sil-portera", "url": "https://supplychains.ru/blog/model-pyati-sil-portera"},
    {"slug": "supplychains-kak-vybirat-postavschikov", "url": "https://supplychains.ru/blog/supplychains-kak-vybirat-postavschikov"},
    {"slug": "kak-otsenit-riski-postavschika", "url": "https://supplychains.ru/blog/kak-otsenit-riski-postavschika"},
    {"slug": "tendernye-zakupki", "url": "https://supplychains.ru/blog/tendernye-zakupki"},
    {"slug": "supply-chain-strategy", "url": "https://supplychains.ru/blog/supply-chain-strategy"},
    {"slug": "5-prichin-pochemu-postavschik-mozhet-sorvat-sroki", "url": "https://supplychains.ru/blog/5-prichin-pochemu-postavschik-mozhet-sorvat-sroki"},
    {"slug": "kak-vybrat-transportnuyu-kompaniyu", "url": "https://supplychains.ru/blog/kak-vybrat-transportnuyu-kompaniyu"},
    {"slug": "sklog-otzyv", "url": "https://supplychains.ru/blog/sklog-otzyv"},
    {"slug": "kak-oformit-gruz", "url": "https://supplychains.ru/blog/kak-oformit-gruz"},
    {"slug": "chto-takoe-in-kot", "url": "https://supplychains.ru/blog/chto-takoe-in-kot"},
    {"slug": "logistika-i-sklad", "url": "https://supplychains.ru/blog/logistika-i-sklad"},
    {"slug": "strategiya-zakupok", "url": "https://supplychains.ru/blog/strategiya-zakupok"},
    {"slug": "5-veschey-kotorye-nuzhno-znat", "url": "https://supplychains.ru/blog/5-veschey-kotorye-nuzhno-znat"},
]

# Количество дней до повторной публикации статьи
ARTICLE_COOLDOWN_DAYS = 30

# === Расписание публикаций (автономный режим) ===
# Время: 11:00 МСК

CONTENT_SCHEDULE = {
    "monday": {
        "type": "news",
        "title_emoji": "🎮",
        "title": "Game Digest",
        "description": "Новости геймификации и игр в логистику. Источник: поиск по всему миру (кроме UA/PL), перевод на RU.",
        "search_queries": [
            "serious games supply chain 2026",
            "logistics simulation training business",
            "business war games supply chain",
            "геймификация обучение логистика",
            "supply chain simulation game corporate training",
            "procurement negotiation game",
            "inventory management simulation",
            "bullwhip effect game education"
        ],
        "hashtags": "#логистика #геймификация #обучение #supplychain #seriousgames",
        "time": "11:00",
        "cta": "🎮 Хотите попробовать игры в логистику? \n👉 https://logistoria.com/index-ru.html",
        "auto_generate": True
    },
    "tuesday": {
        "type": "supplychains_digest",
        "title_emoji": "🚀",
        "title": "Logistics WOW",
        "description": "Выжимка из статей supplychains.ru — читаем в день публикации.",
        "source": "supplychains.ru",
        "hashtags": "#логистика #закупки #цепочкипоставок #supplychains",
        "time": "11:00",
        "cta": "📚 Читать полностью: {article_url}",
        "auto_generate": True
    },
    "wednesday": {
        "type": "promo",
        "topic": "logistoria_game",
        "title_emoji": "📢",
        "title": "Попробуй игру",
        "description": "Анонс игры с logistoria.com — по очереди все игры.",
        "games_rotation": [
            "kadena",
            "thebeergame", 
            "auction_bot",
            "storewars",
            "heroes_rack",
            "market_plays",
            "logistics_course"
        ],
        "hashtags": "#logistoria #симуляция #обучение #игрывлогистику",
        "time": "11:00",
        "cta": "🎮 Заказать игру: https://logistoria.com/{game_url}",
        "auto_generate": True
    },
    "thursday": {
        "type": "supplychains_digest",
        "title_emoji": "🚀",
        "title": "Logistics WOW",
        "description": "Выжимка из статей supplychains.ru — читаем в день публикации.",
        "source": "supplychains.ru",
        "hashtags": "#логистика #закупки #цепочкипоставок #supplychains",
        "time": "11:00",
        "cta": "📚 Читать полностью: {article_url}",
        "auto_generate": True
    },
    "friday": {
        "type": "book_review",
        "topic": "logist_books",
        "title_emoji": "📚",
        "title": "Полка логиста",
        "description": "Книга или фильм про логистику — художественный, научный, бизнес.",
        "books_rotation": [
            {"title": "Цель. Процесс непрерывного совершенствования", "author": "Элияху Голдратт", "type": "business", "teaser": "Теория ограничений через роман. Как найти узкое место в любом процессе."},
            {"title": "The Box", "author": "Marc Levinson", "type": "business", "teaser": "История контейнера, которая изменила мировую торговлю."},
            {"title": "Logistics Clusters", "author": "Yossi Sheffi", "type": "business", "teaser": "Почему логистические хабы концентрируются в одних местах."},
            {"title": "Dunkirk", "type": "film", "teaser": "Логистика эвакуации: как организовать выход 330 000 солдат за 9 дней."},
            {"title": "The Martian", "type": "film", "teaser": "Ресурсная логистика: выживание на Марсе с запасами на 300 солов."},
            {"title": "Essentials of Supply Chain Management", "author": "Michael Hugos", "type": "science", "teaser": "Фундаментальный учебник по SCM для практиков."},
            {"title": "Nефтяной король / King of Oil", "author": "Daniel Ammann", "type": "business", "teaser": "Как фрахт, прогнозирование и поставки сделали из трейдера миллиардера."},
            {"title": "Основатель", "type": "film", "teaser": "История Макдональдс: Just in Time и скорость реакции в QSR."}
        ],
        "hashtags": "#книги #логистика #бизнес #обучение #фильмы",
        "time": "11:00",
        "auto_generate": True
    },
    "saturday": {
        "type": "silence",
        "title_emoji": "🤫",
        "title": "Тишина",
        "description": "Выходной. Постов нет.",
        "auto_generate": False
    },
    "sunday": {
        "type": "digest",
        "topic": "weekly_best",
        "title_emoji": "🔥",
        "title": "Итоги недели",
        "description": "Краткий дайджест: о чём писали на @supplychains на этой неделе.",
        "hashtags": "#итогинедели #лучшее #логистика #supplychains",
        "time": "11:00",
        "auto_generate": True
    }
}

# === Автоматические настройки ===
AUTO_POST = True  # Бот сам публикует без согласования
ADMIN_APPROVAL = False  # Не требовать подтверждение админа

# === Лимиты ===
MAX_POST_LENGTH = 3000
SUMMARY_LENGTH = 800  # Длина выжимки из статьи

# === Форматы постов ===
POST_TEMPLATES = {
    "news": (
        "{emoji} *{title}*\n\n"
        "{content}\n\n"
        "{hashtags}\n\n"
        "{cta}"
    ),
    "supplychains_digest": (
        "{emoji} *{title}*\n\n"
        "📖 *{article_title}*\n\n"
        "{summary}\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    "promo": (
        "{emoji} *{game_name}*\n\n"
        "{description}\n\n"
        "✨ *Чему учит:*\n{teaches}\n\n"
        "👥 *{players}* | ⏱ *{duration}*\n\n"
        "{cta}\n\n"
        "{hashtags}"
    ),
    "book_review": (
        "{emoji} *Полка логиста: {book_title}*\n\n"
        "✍️ *Автор:* {author}\n"
        "🎭 *Жанр:* {genre}\n\n"
        "{teaser}\n\n"
        "{hashtags}"
    ),
    "digest": (
        "{emoji} *Итоги недели*\n\n"
        "📅 *Что обсуждали на @supplychains:*\n\n"
        "{summary}\n\n"
        "📢 *На следующей неделе:*\n"
        "{next_week}\n\n"
        "Не пропустите! Подписывайтесь и жмите 🔔"
    )
}
