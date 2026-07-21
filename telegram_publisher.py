"""Публикация постов в Telegram канал."""

import logging
from typing import Dict, Optional

from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramPublisher:
    """Публикация отформатированных постов в канал."""
    
    def __init__(self, bot: Bot, channel_id: str):
        self.bot = bot
        self.channel_id = channel_id
    
    async def publish(self, post: Dict) -> bool:
        """Опубликовать пост в канал."""
        try:
            text = post.get('text', '')
            image_url = post.get('image_url')
            image_path = post.get('image_path')
            
            # Определяем тип контента
            if image_path:
                # Локальное изображение
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=photo,
                        caption=text[:1024] if len(text) > 1024 else text,
                        parse_mode="Markdown"
                    )
                    
                    # Если текст длиннее 1024 символов (лимит caption),
                    # отправляем остаток отдельным сообщением
                    if len(text) > 1024:
                        await self.bot.send_message(
                            chat_id=self.channel_id,
                            text=text[1024:4096],
                            parse_mode="Markdown"
                        )
                        
            elif image_url:
                # URL изображения
                await self.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=image_url,
                    caption=text[:1024] if len(text) > 1024 else text,
                    parse_mode="Markdown"
                )
                
                if len(text) > 1024:
                    await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=text[1024:4096],
                        parse_mode="Markdown"
                    )
                    
            else:
                # Только текст
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text[:4096],
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                )
            
            logger.info(f"✅ Пост опубликован в {self.channel_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Ошибка публикации: {e}")
            return False
    
    async def publish_poll(self, question: str, options: list, explanation: str = None) -> bool:
        """Опубликовать опрос в канал."""
        try:
            await self.bot.send_poll(
                chat_id=self.channel_id,
                question=question,
                options=options,
                is_anonymous=False,
                allows_multiple_answers=False,
                explanation=explanation
            )
            return True
        except TelegramError as e:
            logger.error(f"Ошибка публикации опроса: {e}")
            return False
    
    async def edit_post(self, message_id: int, new_text: str) -> bool:
        """Редактировать опубликованный пост."""
        try:
            await self.bot.edit_message_text(
                chat_id=self.channel_id,
                message_id=message_id,
                text=new_text[:4096],
                parse_mode="Markdown"
            )
            return True
        except TelegramError as e:
            logger.error(f"Ошибка редактирования: {e}")
            return False
    
    async def delete_post(self, message_id: int) -> bool:
        """Удалить пост из канала."""
        try:
            await self.bot.delete_message(
                chat_id=self.channel_id,
                message_id=message_id
            )
            return True
        except TelegramError as e:
            logger.error(f"Ошибка удаления: {e}")
            return False
