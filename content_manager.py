"""Управление контентом: шаблоны, форматирование, архив."""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ContentManager:
    """Управление шаблонами и форматированием постов."""
    
    # Шаблоны для разных типов постов
    TEMPLATES = {
        "news": {
            "emoji": "📰",
            "structure": [
                "{emoji} *{title}*\n\n",
                "{summary}\n\n",
                "🔍 *Подробности:*\n{details}\n\n",
                "💡 *Что это значит:*\n{implication}\n\n",
                "Источник: {source}\n",
                "#{hashtags}"
            ]
        },
        "game_review": {
            "emoji": "🎮",
            "structure": [
                "{emoji} *Обзор игры: {title}*\n\n",
                "🎯 *Для чего:* {purpose}\n",
                "👥 *Количество участников:* {players}\n",
                "⏱ *Длительность:* {duration}\n\n",
                "📋 *Чему учит:*\n{teaches}\n\n",
                "💬 *Отзыв клиента:*\n\"{testimonial}\"\n\n",
                "🎓 *Попробовать:* {link}\n",
                "#{hashtags}"
            ]
        },
        "case_study": {
            "emoji": "💼",
            "structure": [
                "{emoji} *Кейс: {company}*\n\n",
                "🎯 *Задача:*\n{challenge}\n\n",
                "💡 *Решение:*\n{solution}\n\n",
                "📊 *Результаты:*\n{results}\n\n",
                "🎮 *Использованные игры:*\n{games}\n\n",
                "Хотите так же? {cta}\n",
                "#{hashtags}"
            ]
        },
        "quiz": {
            "emoji": "🧩",
            "structure": [
                "{emoji} *Викторина: {title}*\n\n",
                "{question}\n\n",
                "Варианты:\n",
                "A) {option_a}\n",
                "B) {option_b}\n",
                "C) {option_c}\n",
                "D) {option_d}\n\n",
                "Ответ завтра в 10:00! 👇\n\n",
                "А пока — ваша версия?\n",
                "#{hashtags}"
            ]
        },
        "tips": {
            "emoji": "💡",
            "structure": [
                "{emoji} *Лайфхак: {title}*\n\n",
                "{tip}\n\n",
                "✅ *Как применить:*\n{how_to}\n\n",
                "⚠️ *Ошибки, которых избежать:*\n{mistakes}\n\n",
                "Пробовали такое? Расскажите в комментариях! 👇\n",
                "#{hashtags}"
            ]
        },
        "weekly_digest": {
            "emoji": "📅",
            "structure": [
                "{emoji} *Дайджест недели: {week}*\n\n",
                "🚀 *Главные события:*\n{headlines}\n\n",
                "📚 *Новые материалы:*\n{materials}\n\n",
                "🎮 *Ближайшие демо:*\n{demos}\n\n",
                "Подписывайтесь, чтобы не пропускать! 🔔\n",
                "#{hashtags}"
            ]
        }
    }
    
    # Готовые темы для постов (ротация)
    CONTENT_CALENDAR = [
        {"day": "monday", "type": "news", "topic": "logistics_tech"},
        {"day": "tuesday", "type": "game_review", "topic": "serious_games"},
        {"day": "wednesday", "type": "case_study", "topic": "education"},
        {"day": "thursday", "type": "tips", "topic": "marketplaces"},
        {"day": "friday", "type": "quiz", "topic": "trends"},
        {"day": "saturday", "type": "news", "topic": "trends"},
        {"day": "sunday", "type": "weekly_digest", "topic": "all"},
    ]
    
    def get_template(self, post_type: str) -> Optional[Dict]:
        """Получить шаблон по типу."""
        return self.TEMPLATES.get(post_type)
    
    def format_post(self, post_type: str, data: Dict) -> str:
        """Форматировать пост по шаблону."""
        template = self.TEMPLATES.get(post_type)
        if not template:
            return data.get('text', '')
        
        structure = template['structure']
        text = ''.join(structure)
        
        try:
            return text.format(emoji=template['emoji'], **data)
        except KeyError as e:
            # Если не все поля заполнены — используем базовый текст
            return data.get('text', f"📰 *{data.get('title', 'Новый пост')}*\n\n{data.get('summary', '')}")
    
    def get_daily_theme(self, weekday: int) -> Dict:
        """Получить тему дня (0=Monday)."""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = days[weekday]
        
        for item in self.CONTENT_CALENDAR:
            if item['day'] == day_name:
                return item
        
        return {"day": day_name, "type": "news", "topic": "logistics_tech"}
    
    def generate_hashtags(self, topic: str) -> str:
        """Генерировать хештеги по теме."""
        tags = {
            "logistics_tech": "логистика технологии AI цепипоставок",
            "serious_games": "seriousgames обучение логистика симуляция",
            "education": "образование логистика вузы корпоративноеобучение",
            "marketplaces": "маркетплейсы wildberries ozon ecom",
            "trends": "тренды логистика reshoring устойчивоеразвитие"
        }
        
        base_tags = tags.get(topic, "логистика цепипоставок")
        return ' '.join([f"#{t}" for t in base_tags.split()])
    
    def add_call_to_action(self, post: Dict, cta_type: str = "default") -> str:
        """Добавить призыв к действию."""
        ctas = {
            "default": "\n\n💬 Как вы решаете эту задачу? Делитесь в комментариях!",
            "demo": "\n\n🎮 Хотите попробовать в деле? Запишитесь на демо: https://logistoria.com",
            "download": "\n\n📥 Скачайте материалы по ссылке в шапке профиля",
            "subscribe": "\n\n🔔 Подписывайтесь, чтобы не пропускать разборы кейсов",
            "poll": "\n\n👇 Голосуйте в опросе ниже!"
        }
        
        text = post.get('text', '')
        return text + ctas.get(cta_type, ctas["default"])
