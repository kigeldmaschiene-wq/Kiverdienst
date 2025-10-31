import logging
from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
    
    async def run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        try:
            self.logger.info(f"Starting task: {task_data.get('task_type', 'unknown')}")
            result = await self._execute(task_data)
            self.logger.info(f"Task completed successfully")
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            return {"success": False, "error": str(e)}
    
    @abstractmethod
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        """Implementation of the agent's logic"""
        pass
