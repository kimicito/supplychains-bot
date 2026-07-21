"""SupplyChains Bot — Telegram бот для канала об играх в логистику."""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from news_fetcher import NewsFetcher
from content_manager import ContentManager

# === Конфигурация ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")  # Твой личный chat_id для согласования
CHANNEL_ID = os.getenv("CHANNEL_ID", "@supplychains")

# Директории
BASE_DIR = Path(__file__).parent
DRAFT_DIR = BASE_DIR / "content" / "draft"
APPROVED_DIR = BASE_DIR / "content" / "approved"
PUBLISHED_DIR = BASE_DIR / "content" / "published"
SCHEDULED_DIR = BASE_DIR / "scheduled"

for d in [DRAFT_DIR, APPROVED_DIR, PUBLISHED_DIR, SCHEDULED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupplyChainsBot:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.content_manager = ContentManager()
        self.application: Optional[Application] = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие админа."""
        await update.message.reply_text(
            "🤖 *SupplyChains Bot* запущен!\n\n"
            "Я буду:\n"
            "• Искать новости по логистике и играм\n"
            "• Готовить посты по шаблонам\n"
            "• Присылать тебе на согласование\n"
            "• Публиковать в канал @supplychains\n\n"
            "Команды:\n"
            "/schedule — запланированные посты\n"
            "/force_fetch — найти новости сейчас\n"
            "/stats — статистика канала\n"
            "/help — справка",
            parse_mode="Markdown"
        )

    async def force_fetch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Принудительный поиск новостей."""
        await update.message.reply_text("🔍 Ищу свежие новости...")
        
        posts = await self.news_fetcher.fetch_all()
        
        if not posts:
            await update.message.reply_text("❌ Новостей не найдено. Попробуй позже.")
            return
        
        await update.message.reply_text(f"✅ Найдено {len(posts)} тем. Формирую черновики...")
        
        for i, post in enumerate(posts[:3], 1):  # Максимум 3 за раз
            draft_path = DRAFT_DIR / f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.json"
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            # Отправляем админу на согласование
            keyboard = [
                [{"text": "✅ Публиковать", "callback_data": f"publish:{draft_path.name}"},
                 {"text": "✏️ Редактировать", "callback_data": f"edit:{draft_path.name}"}],
                [{"text": "❌ Пропустить", "callback_data": f"skip:{draft_path.name}"},
                 {"text": "⏰ Отложить", "callback_data": f"schedule:{draft_path.name}"}]
            ]
            
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=self._format_draft(post),
                reply_markup={"inline_keyboard": keyboard},
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        
        await update.message.reply_text(f"📨 Отправил {min(len(posts), 3)} черновика на согласование.")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок админа."""
        query = update.callback_query
        await query.answer()
        
        action, filename = query.data.split(":", 1)
        draft_path = DRAFT_DIR / filename
        
        if not draft_path.exists():
            await query.edit_message_text("❌ Черновик не найден (устарел).")
            return
        
        with open(draft_path, 'r', encoding='utf-8') as f:
            post = json.load(f)
        
        if action == "publish":
            # Публикуем в канал
            await self._publish_post(context.bot, post)
            # Перемещаем в published
            published_path = PUBLISHED_DIR / filename
            draft_path.rename(published_path)
            await query.edit_message_text("✅ Опубликовано в канал!")
            
        elif action == "skip":
            draft_path.unlink()
            await query.edit_message_text("❌ Пропущено.")
            
        elif action == "schedule":
            # Перемещаем в scheduled
            scheduled_path = SCHEDULED_DIR / filename
            draft_path.rename(scheduled_path)
            await query.edit_message_text("⏰ Отложено. Используй /schedule для управления.")
            
        elif action == "edit":
            await query.edit_message_text(
                f"✏️ Отправь отредактированный текст.\n\n"
                f"Текущий черновик:\n{post['text'][:500]}...\n\n"
                f"Ответь на это сообщение с новым текстом."
            )

    async def handle_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка редактирования от админа."""
        if not update.message.reply_to_message:
            return
        
        # Сохраняем отредактированный текст
        new_text = update.message.text
        # TODO: связать с черновиком
        await update.message.reply_text("✅ Текст обновлён. Используй /force_fetch для публикации.")

    async def show_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать запланированные посты."""
        scheduled = list(SCHEDULED_DIR.glob("*.json"))
        if not scheduled:
            await update.message.reply_text("📭 Нет запланированных постов.")
            return
        
        text = "📅 *Запланированные посты:*\n\n"
        for i, f in enumerate(sorted(scheduled), 1):
            with open(f, 'r', encoding='utf-8') as fp:
                post = json.load(fp)
            text += f"{i}. {post.get('title', 'Без названия')}\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика канала."""
        published = list(PUBLISHED_DIR.glob("*.json"))
        draft = list(DRAFT_DIR.glob("*.json"))
        scheduled = list(SCHEDULED_DIR.glob("*.json"))
        
        text = (
            "📊 *Статистика бота*\n\n"
            f"✅ Опубликовано: {len(published)}\n"
            f"📝 На согласовании: {len(draft)}\n"
            f"⏰ Запланировано: {len(scheduled)}\n\n"
            f"Канал: {CHANNEL_ID}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def _publish_post(self, bot: Bot, post: dict):
        """Публикация поста в канал."""
        text = post.get('text', '')
        image_url = post.get('image_url')
        
        if image_url:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=text,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )

    def _format_draft(self, post: dict) -> str:
        """Форматирование черновика для админа."""
        return (
            f"📝 *Черновик поста*\n\n"
            f"*Тема:* {post.get('topic', 'Без темы')}\n"
            f"*Источник:* {post.get('source', 'Неизвестен')}\n\n"
            f"{post.get('text', '')[:800]}...\n\n"
            f"Выбери действие:"
        )

    def run(self):
        """Запуск бота."""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
            logger.info("Создай бота через @BotFather и установи переменную окружения.")
            return
        
        if not ADMIN_CHAT_ID:
            logger.warning("⚠️ ADMIN_CHAT_ID не установлен. Согласование работать не будет.")
        
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Обработчики
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("force_fetch", self.force_fetch))
        self.application.add_handler(CommandHandler("schedule", self.show_schedule))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("help", self.start))
        self.application.add_handler(CommandHandler("publish_now", self.force_fetch))
        
        # Callback от кнопок
        self.application.add_handler(CommandHandler("handle_callback", self.handle_callback))
        
        # TODO: добавить CallbackQueryHandler для inline кнопок
        
        logger.info("🚀 Бот запущен!")
        self.application.run_polling()


if __name__ == "__main__":
    bot = SupplyChainsBot()
    bot.run()
