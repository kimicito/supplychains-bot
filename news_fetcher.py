"""Сбор новостей по логистике, играм и цепям поставок."""

import asyncio
import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

import aiohttp

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Поиск и сбор новостей из интернета."""
    
    # Ключевые слова для поиска по категориям
    TOPICS = {
        "logistics_tech": [
            "логистика технологии 2026",
            "supply chain technology",
            "digital logistics",
            "AI logistics",
            "blockchain supply chain"
        ],
        "serious_games": [
            "serious games logistics",
            "business simulation game",
            "обучающие игры логистика",
            "supply chain simulation",
            "business war games"
        ],
        "education": [
            "logistics education",
            "supply chain curriculum",
            "обучение логистике",
            "corporate training logistics",
            "university supply chain program"
        ],
        "marketplaces": [
            "Wildberries logistics",
            "Ozon logistics",
            "marketplace supply chain",
            "e-commerce logistics Russia",
            "FBO FBS DBS"
        ],
        "trends": [
            "supply chain trends 2026",
            "логистика тренды",
            "reshoring nearshoring",
            "green logistics",
            "last mile delivery"
        ]
    }
    
    # RSS-ленты (если доступны)
    RSS_SOURCES = [
        # Можно добавить RSS-ленты логистических СМИ
    ]
    
    async def fetch_all(self) -> List[Dict]:
        """Собрать новости по всем темам."""
        all_posts = []
        
        for topic_name, queries in self.TOPICS.items():
            for query in queries[:2]:  # Ограничиваем для скорости
                try:
                    posts = await self._search_news(query, topic_name)
                    all_posts.extend(posts)
                    await asyncio.sleep(1)  # Не спамим
                except Exception as e:
                    logger.error(f"Ошибка поиска '{query}': {e}")
        
        # Убираем дубликаты по URL
        seen_urls = set()
        unique_posts = []
        for post in all_posts:
            if post.get('url') not in seen_urls:
                seen_urls.add(post.get('url'))
                unique_posts.append(post)
        
        return unique_posts[:5]  # Максимум 5 постов за раз

    async def _search_news(self, query: str, topic: str) -> List[Dict]:
        """Поиск новостей через поисковые движки."""
        posts = []
        
        # Используем web_search через kimi_search
        # TODO: интегрировать с kimi_search когда будет API
        
        # Пока — заглушка с примерами контента
        example_posts = self._get_example_posts(topic)
        
        return example_posts[:2]

    def _get_example_posts(self, topic: str) -> List[Dict]:
        """Примеры постов по теме (заглушка)."""
        templates = {
            "logistics_tech": [
                {
                    "topic": "Технологии",
                    "title": "AI меняет логистику: как нейросети оптимизируют цепи поставок",
                    "text": "🤖 *AI в логистике*\n\nНовое исследование McKinsey показывает, что компании, внедрившие ИИ в логистику, сократили издержки на 15-20%.\n\nКлючевые направления:\n• Прогнозирование спроса\n• Оптимизация маршрутов\n• Управление запасами\n\n💡 Как вы думаете, заменят ли ИИ логистов или станет их инструментом?\n\n#логистика #AI #цепипоставок",
                    "source": "McKinsey",
                    "image_url": None
                }
            ],
            "serious_games": [
                {
                    "topic": "Игры",
                    "title": "The Beer Game: 40 лет классики в обучении логистике",
                    "text": "🍺 *The Beer Game — 40 лет!*\n\nКлассическая симуляция эффекта хлыста (bullwhip effect) от MIT по-прежнему актуальна.\n\nПочему работает:\n✅ Показывает скрытые проблемы цепи поставок\n✅ Командное взаимодействие\n✅ Принятие решений в условиях неопределённости\n\n🎓 Сколько стоит ошибка в прогнозировании? В игре — пара лишних ящиков пива. В реальности — миллионы.\n\nПробовали The Beer Game в своей компании?\n\n#thebeergame #логистика #обучение #симуляция",
                    "source": "MIT",
                    "image_url": None
                }
            ],
            "education": [
                {
                    "topic": "Образование",
                    "title": "Как ВШЭ обучает логистике через игры",
                    "text": "🎓 *Игры в образовании*\n\nВысшая школа экономики запустила новый модуль «Логистика через симуляции». Студенты проходят:\n\n1️⃣ KADENA — управление цепочками поставок\n2️⃣ The Beer Game — эффект хлыста\n3️⃣ Storewars — переговоры и ценообразование\n\n📊 Результаты:\n• Вовлечённость +40%\n• Запоминаемость +65%\n\nКакой формат обучения эффективнее — лекции или игры?\n\n#образование #логистика #вшэ #симуляции",
                    "source": "ВШЭ",
                    "image_url": None
                }
            ],
            "marketplaces": [
                {
                    "topic": "Маркетплейсы",
                    "title": "FBO vs FBS vs DBS: что выбрать продавцу в 2026",
                    "text": "📦 *Модели работы с маркетплейсами*\n\nWildberries, Ozon, Яндекс.Маркет — каждый предлагает свои схемы:\n\n🔹 *FBO* — склады маркетплейса\nПлюсы: логистика на них\nМинусы: меньше контроля\n\n🔹 *FBS* — со своего склада\nПлюсы: контроль остатков\nМинусы: сами доставляете на точки\n\n🔹 *DBS* — доставка силами продавца\nПлюсы: гибкость\nМинусы: сложнее масштабировать\n\nКакая модель у вас? Испытали в игре *MarketPlays*?\n\n#маркетплейсы #wildberries #ozon #fbo #fbs",
                    "source": "Logistoria",
                    "image_url": None
                }
            ],
            "trends": [
                {
                    "topic": "Тренды",
                    "title": "Reshoring: компании возвращают производство домой",
                    "text": "🌍 *Reshoring — новая реальность*\n\nGE, Apple, Intel переносят производство из Китая в США, Мексику, Вьетнам.\n\nПричины:\n• Геополитические риски\n• Рост зарплат в Китае\n• Стремление к устойчивости цепей поставок\n\n📉 Но: производство в США дороже на 30-40%. Как компенсировать?\n\n💡 Автоматизация, ИИ, роботизация — и обучение персонала через симуляции.\n\nКак думаете, какие профессии в логистике будут востребованы через 5 лет?\n\n#reshoring #логистика #тренды #цепипоставок",
                    "source": "Financial Times",
                    "image_url": None
                }
            ]
        }
        
        return templates.get(topic, [])

    async def fetch_by_topic(self, topic: str) -> List[Dict]:
        """Поиск новостей по конкретной теме."""
        queries = self.TOPICS.get(topic, [topic])
        posts = []
        
        for query in queries[:2]:
            try:
                results = await self._search_news(query, topic)
                posts.extend(results)
            except Exception as e:
                logger.error(f"Ошибка: {e}")
        
        return posts[:3]
