"""
Base Agent Class - Foundation for all AI Agents
Every agent in the system inherits from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import json
import time
import asyncpg

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all AI Agents in KIVerdienst
    
    Features:
    - Automatic logging to database
    - Configuration management
    - Timing measurement
    - Error handling
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Main execution method - MUST be implemented by subclass
        
        Returns:
            Dict with at least:
            {
                'success': bool,
                'data': Any,
                'error': str (optional)
            }
        """
        pass
    
    async def log_action(
        self,
        action: str,
        status: str,
        message: str,
        details: Optional[Dict] = None,
        duration_ms: Optional[int] = None,
        brand_id: Optional[int] = None,
        video_id: Optional[int] = None
    ):
        """
        Log agent action to database
        
        Args:
            action: Action name (e.g., 'generate_script', 'select_topics')
            status: 'success', 'failed', 'warning'
            message: Human-readable message
            details: Additional data (stored as JSONB)
            duration_ms: Execution time in milliseconds
            brand_id: Related brand ID (optional)
            video_id: Related video ID (optional)
        """
        try:
            from app.database import get_pool
            
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ai_agents_logs 
                    (agent_name, action, status, message, details, duration_ms, brand_id, video_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, 
                    self.name, 
                    action, 
                    status, 
                    message,
                    json.dumps(details) if details else None,
                    duration_ms, 
                    brand_id, 
                    video_id
                )
            
            # Also log to file
            if status == 'failed':
                self.logger.error(f"{action}: {message}")
            elif status == 'warning':
                self.logger.warning(f"{action}: {message}")
            else:
                self.logger.info(f"{action}: {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to log action: {e}")
    
    async def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value from settings table
        
        Args:
            key: Setting key (e.g., 'runway_api_key')
            default: Default value if not found
        
        Returns:
            Configuration value or default
        """
        try:
            from app.database import get_pool
            
            pool = await get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow("SELECT value FROM settings WHERE key = $1", key)
                
                if result:
                    try:
                        return json.loads(result['value'])
                    except:
                        return result['value']
                return default
            
        except Exception as e:
            self.logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def measure_time(self):
        """
        Context manager for timing operations
        
        Usage:
            with self.measure_time() as timer:
                # do work
                pass
            
            duration = timer.duration_ms
        """
        return TimingContext()

class TimingContext:
    """Context manager for measuring execution time"""
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        self.end = time.time()
        self.duration_ms = int((self.end - self.start) * 1000)
