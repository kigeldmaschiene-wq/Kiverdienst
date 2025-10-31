import logging
from typing import Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    async def run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with error handling"""
        try:
            self.logger.info(f"Task started: {task_data.get('type', 'unknown')}")
            result = await self._execute(task_data)
            self.logger.info("Task completed successfully")
            return {
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @abstractmethod
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        """Execute the actual agent logic - must be implemented by subclasses"""
        pass
