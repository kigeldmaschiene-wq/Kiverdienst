from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import json
import time

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        pass
    
    async def log_action(self, action: str, status: str, message: str, 
                        details: Optional[Dict] = None, duration_ms: Optional[int] = None,
                        brand_id: Optional[int] = None, video_id: Optional[int] = None):
        try:
            import psycopg2.extras
            from app.database import get_db
            
            db = get_db()
            cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                INSERT INTO ai_agents_logs 
                (agent_name, action, status, message, details, duration_ms, brand_id, video_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.name, action, status, message, 
                  json.dumps(details) if details else None,
                  duration_ms, brand_id, video_id))
            
            db.commit()
            cursor.close()
        except Exception as e:
            self.logger.error(f"Failed to log: {e}")
    
    def measure_time(self):
        return TimingContext()

class TimingContext:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        self.duration_ms = int((time.time() - self.start) * 1000)
