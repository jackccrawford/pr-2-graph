from typing import Dict, List, Type
from ..plugins.base import BasePlugin, PluginConfig


class PluginRegistry:
    """Registry for managing plugins"""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
    
    def register_plugin(self, plugin_class: Type[BasePlugin], config: PluginConfig):
        """Register a plugin class with configuration"""
        plugin_name = config.name
        self._plugin_classes[plugin_name] = plugin_class
        self._plugins[plugin_name] = plugin_class(config)
    
    def get_plugin(self, name: str) -> BasePlugin:
        """Get a plugin by name"""
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not found")
        return self._plugins[name]
    
    def list_plugins(self) -> List[Dict[str, any]]:
        """List all registered plugins"""
        return [
            {
                "name": plugin.config.name,
                "version": plugin.config.version,
                "description": plugin.config.description,
                "enabled": plugin.config.enabled,
                "schema": plugin.get_schema()
            }
            for plugin in self._plugins.values()
        ]
    
    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get all enabled plugins"""
        return [plugin for plugin in self._plugins.values() if plugin.is_enabled()]


plugin_registry = PluginRegistry()
