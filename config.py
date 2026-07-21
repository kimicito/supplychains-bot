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

# === Расписание публикаций (автономный режим) ===
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
        "hashtags": "#логистика #геймификация #обучение #supplychain # seriousgames",
        "time": "09:00",
        "cta": "🎮 Хотите попробовать игры в логистику? \n👉 https://logistoria.com/index-ru.html",
        "auto_generate": True
    },
    "tuesday": {
        "type": "supplychains_digest",
        "title_emoji": "🚀",
        "title": "Logistics WOW",
        "description": "Выжимка из статей supplychains.ru — статьи про закупки, логистику, цепочки поставок.",
        "source": "supplychains.ru",
        "hashtags": "#логистика #закупки #цепочкипоставок #supplychains",
        "time": "09:00",
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
        "time": "09:00",
        "cta": "🎮 Заказать игру: https://logistoria.com/{game_url}",
        "auto_generate": True
    },
    "thursday": {
        "type": "supplychains_digest",
        "title_emoji": "🚀",
        "title": "Logistics WOW",
        "description": "Выжимка из статей supplychains.ru — новая статья.",
        "source": "supplychains.ru",
        "hashtags": "#логистика #закупки #цепочкипоставок #supplychains",
        "time": "09:00",
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
        "time": "09:00",
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
        "time": "10:00",
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
