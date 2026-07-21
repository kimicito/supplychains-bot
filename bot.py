"""SupplyChains Bot — полностью автономный бот для @supplychains."""

import os
import json
import asyncio
import logging
import random
import re
from datetime import datetime, timedelta, time as dt_time, timezone
from pathlib import Path
from dotenv import load_dotenv

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import (
    CONTENT_SCHEDULE, POST_TEMPLATES, CHANNEL_ID,
    SUPPLYCHAINS_URL, LOGISTORIA_URL, AUTO_POST,
    ARTICLES_DATABASE, SUMMARY_LENGTH
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "143946238")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Директории
BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content"
PUBLISHED_DIR = CONTENT_DIR / "published"
SCHEDULED_DIR = CONTENT_DIR / "scheduled"
for d in [CONTENT_DIR, PUBLISHED_DIR, SCHEDULED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Состояние
STATE_FILE = BASE_DIR / "bot_state.json"


def load_state():
    """Загрузить состояние бота."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_posts": {},
        "game_index": 0,
        "book_index": 0,
        "article_index": 0,
        "article_cache": []
    }


def save_state(state):
    """Сохранить состояние бота."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_today_schedule():
    """Получить расписание на сегодня."""
    weekday = datetime.now().strftime("%A").lower()
    return CONTENT_SCHEDULE.get(weekday)


class AutonomousBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.state = load_state()
        self._setup_handlers()
        
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("generate", self.cmd_generate))
        self.app.add_handler(CommandHandler("post_now", self.cmd_post_now))
        self.app.add_handler(CommandHandler("schedule", self.cmd_schedule))
        self.app.add_handler(CommandHandler("stats", self.cmd_stats))
        
        # Настройка ежедневного задания — 11:00 МСК
        self.app.job_queue.run_daily(
            self._daily_post_job,
            time=dt_time(hour=11, minute=0, tzinfo=timezone(timedelta(hours=3)))  # MSK
        )
        logger.info("📅 Автопубликация настроена: 11:00 MSK")
        
    async def _daily_post_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Ежедневная публикация по расписанию."""
        schedule = get_today_schedule()
        if not schedule or not schedule.get('auto_generate', False):
            logger.info(f"Сегодня выходной или нет расписания")
            return
            
        logger.info(f"📝 Автогенерация: {schedule['title']}")
        
        try:
            post = await self._generate_post(schedule)
            
            # Сохраняем
            post_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            post_path = SCHEDULED_DIR / f"{post_id}.json"
            with open(post_path, 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            # Публикуем
            await self._publish_to_channel(context.bot, post)
            
            # Перемещаем в published
            published_path = PUBLISHED_DIR / f"{post_id}.json"
            post_path.rename(published_path)
            
            logger.info(f"✅ Опубликовано: {schedule['title']}")
            
            # Уведомляем админа
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"✅ Автопубликация завершена\n\n*{schedule['title_emoji']} {schedule['title']}*\n\nОпубликовано в {CHANNEL_ID}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка автопубликации: {e}")
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"❌ Ошибка автопубликации: {str(e)[:200]}"
            )
        
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_admin = str(update.effective_user.id) == ADMIN_CHAT_ID
        if not is_admin:
            await update.message.reply_text("Бот только для администратора.")
            return
            
        await update.message.reply_text(
            f"🤖 *SupplyChains Bot — Автономный режим*\n\n"
            f"Канал: {CHANNEL_ID}\n"
            f"Режим: {'Авто-публикация' if AUTO_POST else 'Согласование'}\n\n"
            f"📅 *Расписание (11:00 МСК):*\n"
            f"Пн — 🎮 Game Digest\n"
            f"Вт — 🚀 Logistics WOW (читаем статью)\n"
            f"Ср — 📢 Попробуй игру\n"
            f"Чт — 🚀 Logistics WOW (читаем статью)\n"
            f"Пт — 📚 Полка логиста\n"
            f"Сб — 🤫 Тишина\n"
            f"Вс — 🔥 Итоги недели\n\n"
            f"Команды:\n"
            f"/generate — создать пост на сегодня\n"
            f"/post_now — опубликовать немедленно\n"
            f"/schedule — расписание\n"
            f"/stats — статистика",
            parse_mode="Markdown"
        )
        
    async def cmd_generate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_admin = str(update.effective_user.id) == ADMIN_CHAT_ID
        if not is_admin:
            return
            
        schedule = get_today_schedule()
        if not schedule:
            await update.message.reply_text("На сегодня расписание не настроено.")
            return
            
        if not schedule.get('auto_generate', False):
            await update.message.reply_text(f"Сегодня {schedule['title']} — выходной.")
            return
            
        await update.message.reply_text(
            f"📝 Генерирую: *{schedule['title_emoji']} {schedule['title']}*...",
            parse_mode="Markdown"
        )
        
        post = await self._generate_post(schedule)
        
        # Сохраняем
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        post_path = SCHEDULED_DIR / f"{post_id}.json"
        with open(post_path, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
            
        # Показываем админу
        await update.message.reply_text(
            f"✅ Пост создан:\n\n{post['text'][:1200]}...",
            parse_mode="Markdown"
        )
        
        if AUTO_POST:
            await self._publish_to_channel(context.bot, post)
            published_path = PUBLISHED_DIR / f"{post_id}.json"
            post_path.rename(published_path)
            await update.message.reply_text("✅ Опубликовано в канал!")
        
    async def cmd_post_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Опубликовать последний созданный пост."""
        is_admin = str(update.effective_user.id) == ADMIN_CHAT_ID
        if not is_admin:
            return
            
        posts = sorted(SCHEDULED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not posts:
            await update.message.reply_text("Нет готовых постов. Используй /generate")
            return
            
        with open(posts[0], 'r', encoding='utf-8') as f:
            post = json.load(f)
            
        await self._publish_to_channel(context.bot, post)
        
        published_path = PUBLISHED_DIR / posts[0].name
        posts[0].rename(published_path)
        
        await update.message.reply_text("✅ Опубликовано!")
        
    async def cmd_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "📅 *Расписание публикаций (11:00 МСК):*\n\n"
        for day, cfg in CONTENT_SCHEDULE.items():
            if cfg.get('auto_generate', False):
                text += f"{cfg['title_emoji']} *{day.capitalize()}* — {cfg['title']}\n"
            else:
                text += f"{cfg['title_emoji']} *{day.capitalize()}* — {cfg['title']} (выходной)\n"
        await update.message.reply_text(text, parse_mode="Markdown")
        
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        published = list(PUBLISHED_DIR.glob("*.json"))
        scheduled = list(SCHEDULED_DIR.glob("*.json"))
        
        types = {}
        for p in published:
            with open(p, 'r') as f:
                data = json.load(f)
                t = data.get('type', 'unknown')
                types[t] = types.get(t, 0) + 1
                
        type_stats = "\n".join([f"  {k}: {v}" for k, v in types.items()])
        
        text = (
            f"📊 *Статистика*\n\n"
            f"✅ Опубликовано: {len(published)}\n"
            f"📝 В очереди: {len(scheduled)}\n\n"
            f"*По типам:*\n{type_stats}\n\n"
            f"📢 Канал: {CHANNEL_ID}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
        
    async def _generate_post(self, schedule: dict) -> dict:
        """Генерация поста по расписанию."""
        post_type = schedule['type']
        
        generators = {
            "news": self._generate_news_post,
            "supplychains_digest": self._generate_supplychains_post,
            "promo": self._generate_promo_post,
            "book_review": self._generate_book_post,
            "digest": self._generate_digest_post
        }
        
        generator = generators.get(post_type, self._generate_news_post)
        return await generator(schedule)
        
    async def _generate_news_post(self, schedule: dict) -> dict:
        """Генерация Game Digest — новости из мира геймификации."""
        queries = schedule.get('search_queries', [])
        query = random.choice(queries) if queries else "serious games logistics"
        
        topics = [
            {
                "title": "Как геймификация меняет корпоративное обучение",
                "fact": "Компании, использующие игровые симуляции, сокращают время адаптации новых сотрудников на 40%."
            },
            {
                "title": "Business War Games: когда бизнес учится на ошибках",
                "fact": "Крупнейшие консалтинговые компании (McKinsey, BCG) регулярно используют симуляции для стратегического планирования."
            },
            {
                "title": "Почему The Beer Game до сих пор актуален",
                "fact": "Эффект хлыста (bullwhip effect) ежегодно обходится ритейлерам в $100+ млрд из-за неоптимальных запасов."
            },
            {
                "title": "Складская логистика: от игры к реальности",
                "fact": "Amazon обрабатывает 1.6 млн заказов в час в пиковые дни — благодаря алгоритмам, которые можно изучить через симуляции."
            }
        ]
        
        topic = random.choice(topics)
        
        return {
            "type": "news",
            "title": f"{schedule['title_emoji']} {schedule['title']}",
            "text": (
                f"{schedule['title_emoji']} *{topic['title']}*\n\n"
                f"💡 *Факт дня:*\n{topic['fact']}\n\n"
                f"🌍 Геймификация в бизнесе набирает обороты: от закупок до логистики, от переговоров до стратегического планирования.\n\n"
                f"Какую игру пробовали в вашей компании?\n\n"
                f"{schedule['hashtags']}\n\n"
                f"{schedule.get('cta', '')}"
            ),
            "topic": schedule['topic'] if 'topic' in schedule else 'game_digest',
            "created_at": datetime.now().isoformat()
        }
        
    async def _generate_supplychains_post(self, schedule: dict) -> dict:
        """Генерация выжимки из supplychains.ru — читаем статью в день публикации."""
        # Получаем следующую статью из ротации
        idx = self.state.get('article_index', 0) % len(ARTICLES_DATABASE)
        article = ARTICLES_DATABASE[idx]
        
        logger.info(f"📖 Читаем статью: {article['url']}")
        
        # Читаем статью в реальном времени
        try:
            title, summary = await self._fetch_article_content(article['url'])
            logger.info(f"✅ Статья прочитана: {title}")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения статьи: {e}")
            # Fallback — используем slug как заголовок
            title = article['slug'].replace('-', ' ').title()
            summary = "Читайте полную версию статьи на сайте."
        
        # Обновляем индекс
        self.state['article_index'] = idx + 1
        save_state(self.state)
        
        # Формируем CTA
        cta = schedule.get('cta', '').format(article_url=article['url'])
        
        # Обрезаем summary
        if len(summary) > SUMMARY_LENGTH:
            summary = summary[:SUMMARY_LENGTH].rsplit(' ', 1)[0] + "..."
        
        return {
            "type": "supplychains_digest",
            "title": f"{schedule['title_emoji']} {schedule['title']}",
            "text": (
                f"{schedule['title_emoji']} *{title}*\n\n"
                f"{summary}\n\n"
                f"{cta}\n\n"
                f"{schedule['hashtags']}"
            ),
            "topic": "supplychains_digest",
            "article_url": article['url'],
            "article_slug": article['slug'],
            "created_at": datetime.now().isoformat()
        }
        
    async def _fetch_article_content(self, url: str) -> tuple:
        """Прочитать статью с supplychains.ru через aiohttp."""
        import aiohttp
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")
                
                html = await resp.text()
                
                # Парсим заголовок (H1)
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else "Статья"
                # Убираем HTML-теги из заголовка
                title = re.sub(r'<[^>]+>', '', title)
                
                # Парсим основной текст
                # Ищем блоки с текстом статьи (типичная структура Tilda)
                text_blocks = []
                
                # Пробуем найти основной контент через разные селекторы
                # Вариант 1: t-feed__post-wrapper
                content_match = re.search(r'class="t-feed__post-wrapper[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)
                if content_match:
                    text = content_match.group(1)
                else:
                    # Вариант 2: любой большой блок текста
                    text = html
                
                # Извлекаем текст из параграфов
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text, re.DOTALL)
                
                for p in paragraphs:
                    # Убираем HTML-теги
                    clean = re.sub(r'<[^>]+>', '', p)
                    # Убираем лишние пробелы
                    clean = ' '.join(clean.split())
                    # Пропускаем короткие и служебные
                    if len(clean) > 30 and not any(skip in clean.lower() for skip in ['cookie', 'подписаться', 'рекомендуем', 'читайте также']):
                        text_blocks.append(clean)
                
                # Собираем summary из первых 3-5 абзацев
                summary = ' '.join(text_blocks[:5])
                
                # Если не получилось — берём любой текст
                if not summary:
                    # Убираем все теги и берём первые 500 символов
                    plain = re.sub(r'<[^>]+>', ' ', html)
                    plain = ' '.join(plain.split())
                    # Ищем начало осмысленного текста
                    words = plain.split()
                    # Пропускаем первые ~50 слов (обычно меню/шапка)
                    start = min(50, len(words)//4)
                    summary = ' '.join(words[start:start+150])
                
                return title, summary
        
    async def _generate_promo_post(self, schedule: dict) -> dict:
        """Анонс игры logistoria.com."""
        games = schedule.get('games_rotation', [])
        if not games:
            games = ['kadena']
            
        idx = self.state.get('game_index', 0) % len(games)
        game = games[idx]
        self.state['game_index'] = idx + 1
        save_state(self.state)
        
        game_data = {
            "kadena": {
                "name": "KADENA",
                "url": "kadena-ru.html",
                "desc": "Онлайн-симуляция управления цепочками поставок. Командная игра для 8-12 участников.",
                "teaches": "• Понимание взаимосвязей в цепи поставок\n• Управление запасами и прогнозирование\n• Эффект хлыста на практике\n• Командное принятие решений",
                "players": "8-12 человек",
                "duration": "2-3 часа"
            },
            "thebeergame": {
                "name": "The Beer Game",
                "url": "thebeergame-ru.html",
                "desc": "Классическая симуляция эффекта хлыста от MIT. Адаптированная версия для российских компаний.",
                "teaches": "• Эффект хлыста (bullwhip effect)\n• Информационные задержки\n• Координация между звеньями цепи\n• Прогнозирование спроса",
                "players": "4-30 человек",
                "duration": "1.5-2 часа"
            },
            "auction_bot": {
                "name": "Auction Bot",
                "url": "auction-bot-ru.html",
                "desc": "Игра-аукцион в Telegram для обучения закупкам и переговорам.",
                "teaches": "• Переговоры и торги\n• Стратегическое мышление\n• Работа в условиях неопределённости\n• Принятие решений под давлением",
                "players": "4-20 человек",
                "duration": "1 час"
            },
            "storewars": {
                "name": "Storewars",
                "url": "storewars-ru.html",
                "desc": "Симуляция FMCG-рынка: переговоры, ценообразование, логистика, маркетинг.",
                "teaches": "• Коммерческие переговоры\n• Ценообразование и маржа\n• Управление ассортиментом\n• Логистика и дистрибуция",
                "players": "8-16 человек",
                "duration": "3-4 часа"
            },
            "heroes_rack": {
                "name": "Герои стеллажа",
                "url": "heroes-rack-ru.html",
                "desc": "Настольная игра про складскую логистику. Формат Print&Play.",
                "teaches": "• WMS и складские процессы\n• Приоритизация задач\n• Оптимизация маршрутов\n• Работа с ограничениями",
                "players": "2-6 человек",
                "duration": "45-90 минут"
            },
            "market_plays": {
                "name": "MarketPlays",
                "url": "market-plays-ru.html",
                "desc": "Симуляция работы с маркетплейсами: Wildberries, Ozon, Яндекс.Маркет.",
                "teaches": "• FBO, FBS, DBS модели\n• Логистика e-commerce\n• Работа с площадками\n• Управление ассортиментом",
                "players": "6-12 человек",
                "duration": "2 часа"
            },
            "logistics_course": {
                "name": "Курс логистики для школьников",
                "url": "logistics-course-ru.html",
                "desc": "Образовательная программа для старшеклассников и студентов.",
                "teaches": "• Основы логистики\n• Цепи поставок\n• Транспорт и складирование\n• Профессия логиста",
                "players": "15-30 человек",
                "duration": "10 занятий"
            }
        }
        
        g = game_data.get(game, game_data["kadena"])
        cta = schedule.get('cta', '').format(game_url=g['url'])
        
        return {
            "type": "promo",
            "title": f"{schedule['title_emoji']} {schedule['title']}",
            "text": (
                f"{schedule['title_emoji']} *{g['name']}*\n\n"
                f"{g['desc']}\n\n"
                f"✨ *Чему учит:*\n{g['teaches']}\n\n"
                f"👥 *{g['players']}* | ⏱ *{g['duration']}*\n\n"
                f"{cta}\n\n"
                f"{schedule['hashtags']}"
            ),
            "topic": schedule['topic'],
            "created_at": datetime.now().isoformat()
        }
        
    async def _generate_book_post(self, schedule: dict) -> dict:
        """Книга/фильм недели."""
        books = schedule.get('books_rotation', [])
        if not books:
            books = [{"title": "Цель", "author": "Голдратт", "type": "business", "teaser": "Теория ограничений"}]
            
        idx = self.state.get('book_index', 0) % len(books)
        book = books[idx]
        self.state['book_index'] = idx + 1
        save_state(self.state)
        
        genre_map = {
            "business": "Бизнес",
            "science": "Научный",
            "film": "Фильм"
        }
        
        return {
            "type": "book_review",
            "title": f"{schedule['title_emoji']} {schedule['title']}",
            "text": (
                f"{schedule['title_emoji']} *Полка логиста: {book['title']}*\n\n"
                f"✍️ *Автор:* {book.get('author', '—')}\n"
                f"🎭 *Жанр:* {genre_map.get(book.get('type', 'business'), 'Бизнес')}\n\n"
                f"{book.get('teaser', '')}\n\n"
                f"💡 *Почему стоит:*\n"
                f"Каждая неделя — новая книга или фильм про логистику, закупки и цепочки поставок.\n\n"
                f"{schedule['hashtags']}"
            ),
            "topic": schedule['topic'],
            "created_at": datetime.now().isoformat()
        }
        
    async def _generate_digest_post(self, schedule: dict) -> dict:
        """Итоги недели."""
        published = sorted(PUBLISHED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        
        topics = []
        for p in published:
            with open(p, 'r') as f:
                data = json.load(f)
                title = data.get('title', 'Пост')
                topics.append(title)
                
        topics_text = "\n".join([f"• {t}" for t in topics[:3]]) if topics else "• Game Digest\n• Logistics WOW\n• Попробуй игру"
        
        return {
            "type": "digest",
            "title": f"{schedule['title_emoji']} {schedule['title']}",
            "text": (
                f"{schedule['title_emoji']} *Итоги недели на @supplychains*\n\n"
                f"📅 *Что обсуждали:*\n"
                f"{topics_text}\n\n"
                f"📢 *На следующей неделе:*\n"
                f"• 🎮 Game Digest — новости геймификации\n"
                f"• 🚀 Logistics WOW — статьи supplychains.ru\n"
                f"• 📢 Попробуй игру — анонс симуляции\n\n"
                f"Подписывайтесь и жмите 🔔, чтобы не пропустить!"
            ),
            "topic": schedule['topic'],
            "created_at": datetime.now().isoformat()
        }
        
    async def _publish_to_channel(self, bot: Bot, post: dict):
        """Публикация в канал."""
        text = post.get('text', '')
        
        # Разбиваем длинные сообщения
        max_len = 4096
        parts = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        
        for i, part in enumerate(parts):
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=part,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            if i < len(parts) - 1:
                await asyncio.sleep(1)
                
    def run(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
            return
            
        logger.info("🚀 SupplyChains Bot — Автономный режим")
        logger.info(f"📢 Канал: {CHANNEL_ID}")
        logger.info(f"👤 Админ: {ADMIN_CHAT_ID}")
        logger.info(f"⚙️ Авто-публикация: {AUTO_POST}")
        logger.info(f"📅 Время: 11:00 MSK")
        logger.info(f"📖 Статей в ротации: {len(ARTICLES_DATABASE)}")
        self.app.run_polling()


if __name__ == "__main__":
    bot = AutonomousBot()
    bot.run()
