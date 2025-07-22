from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PluginConfig(BaseModel):
    """Configuration for a plugin"""
    name: str
    version: str
    description: str
    enabled: bool = True


class PluginResult(BaseModel):
    """Base result from plugin execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, config: PluginConfig):
        self.config = config
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> PluginResult:
        """Execute the plugin with given input data"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the input/output schema for this plugin"""
        pass
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.config.enabled
