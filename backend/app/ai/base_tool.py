from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel

class BaseAITool(ABC):
    """
    Abstract Base Class for all AI-powered tools inside AgriGenius.
    Each of the 30+ capabilities will inherit from this class.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The tool's unique identifier used by the LLM function calling system."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what the tool does, used for prompt injection."""
        pass
        
    @property
    @abstractmethod
    def parameter_schema(self) -> Type[BaseModel]:
        """Pydantic model describing inputs required to execute the tool."""
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute the tool action asynchronously.
        """
        pass
