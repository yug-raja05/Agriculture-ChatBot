import logging
from typing import Dict, List, Type
from pydantic import ValidationError
from app.ai.base_tool import BaseAITool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Central repository tracking registered agricultural tools.
    Provides standard schemas for LLM routing and validation.
    """
    def __init__(self):
        self._tools: Dict[str, BaseAITool] = {}

    def register(self, tool_instance: BaseAITool) -> None:
        name = tool_instance.name
        if name in self._tools:
            logger.warning(f"Overwriting already registered tool: {name}")
        self._tools[name] = tool_instance
        logger.info(f"Registered AI Tool: {name}")

    def get_tool(self, name: str) -> BaseAITool:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseAITool]:
        return list(self._tools.values())

    def get_tool_definitions_for_llm(self) -> List[dict]:
        """
        Export tool schemas matching typical LLM function calling schemas.
        """
        definitions = []
        for tool in self._tools.values():
            definitions.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameter_schema.model_json_schema()
            })
        return definitions

    async def execute_tool(self, name: str, params: dict, user_id: str) -> dict:
        """
        Resolves a tool, validates parameters, and executes.
        """
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found."}
            
        try:
            # Dynamically validate parameters using the tool's Pydantic schema
            validated_params = tool.parameter_schema(**params)
            # Run the tool
            result = await tool.execute(validated_params.model_dump(), user_id)
            return {"success": True, "result": result}
        except ValidationError as val_err:
            logger.error(f"Parameter validation failed for tool {name}: {str(val_err)}")
            return {"success": False, "error": "Invalid tool arguments.", "details": val_err.errors()}
        except Exception as err:
            logger.error(f"Execution error on tool {name}: {str(err)}")
            return {"success": False, "error": str(err)}

# Central instance to be imported across endpoints and services
ai_tool_registry = ToolRegistry()

def register_tool(tool_instance: BaseAITool):
    """
    Convenience helper/decorator wrapper to register tools on startup.
    """
    ai_tool_registry.register(tool_instance)
    return tool_instance
