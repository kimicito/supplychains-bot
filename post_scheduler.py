"""Планировщик публикаций."""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PostScheduler:
    """Управление расписанием публикаций."""
    
    # Оптимальное время публикаций (МСК)
    BEST_TIMES = {
        "morning": "09:00",    # Начало рабочего дня
        "lunch": "12:30",      # Обеденный перерыв
        "evening": "18:00",    # Конец рабочего дня
        "night": "21:00",      # Вечерний трафик
    }
    
    def __init__(self, scheduled_dir: Path):
        self.scheduled_dir = scheduled_dir
        self.scheduled_dir.mkdir(parents=True, exist_ok=True)
    
    def schedule_post(self, post: Dict, publish_at: datetime) -> str:
        """Запланировать пост на определённое время."""
        post_id = f"scheduled_{publish_at.strftime('%Y%m%d_%H%M%S')}"
        filepath = self.scheduled_dir / f"{post_id}.json"
        
        data = {
            "id": post_id,
            "post": post,
            "scheduled_for": publish_at.isoformat(),
            "status": "pending",  # pending, published, cancelled
            "created_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Пост запланирован на {publish_at}: {post_id}")
        return post_id
    
    def get_pending_posts(self) -> List[Dict]:
        """Получить все ожидающие публикации посты."""
        posts = []
        
        for filepath in sorted(self.scheduled_dir.glob("*.json")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('status') == 'pending':
                    scheduled_time = datetime.fromisoformat(data['scheduled_for'])
                    data['_filepath'] = str(filepath)
                    data['_scheduled_time'] = scheduled_time
                    posts.append(data)
            except Exception as e:
                logger.error(f"Ошибка чтения {filepath}: {e}")
        
        return sorted(posts, key=lambda x: x['_scheduled_time'])
    
    def get_posts_ready_to_publish(self) -> List[Dict]:
        """Получить посты, которые пора публиковать."""
        now = datetime.now()
        ready = []
        
        for post in self.get_pending_posts():
            if post['_scheduled_time'] <= now:
                ready.append(post)
        
        return ready
    
    def mark_published(self, post_id: str):
        """Отметить пост как опубликованный."""
        filepath = self.scheduled_dir / f"{post_id}.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['status'] = 'published'
            data['published_at'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def cancel_post(self, post_id: str) -> bool:
        """Отменить запланированный пост."""
        filepath = self.scheduled_dir / f"{post_id}.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['status'] = 'cancelled'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        return False
    
    def get_optimal_time(self, day_offset: int = 0, time_key: str = "morning") -> datetime:
        """Получить оптимальное время для публикации."""
        now = datetime.now()
        target_date = now + timedelta(days=day_offset)
        
        time_str = self.BEST_TIMES.get(time_key, "09:00")
        hour, minute = map(int, time_str.split(':'))
        
        optimal = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Если время уже прошло, переносим на завтра
        if optimal <= now:
            optimal += timedelta(days=1)
        
        return optimal
    
    def schedule_weekly_plan(self, posts: List[Dict]) -> List[str]:
        """Запланировать посты на неделю вперёд."""
        post_ids = []
        
        for i, post in enumerate(posts):
            # Публикуем в рабочие дни, по одному посту в день
            day_offset = (i % 5) + 1  # Завтра и далее
            time_key = list(self.BEST_TIMES.keys())[i % len(self.BEST_TIMES)]
            
            publish_at = self.get_optimal_time(day_offset, time_key)
            post_id = self.schedule_post(post, publish_at)
            post_ids.append(post_id)
        
        return post_ids
