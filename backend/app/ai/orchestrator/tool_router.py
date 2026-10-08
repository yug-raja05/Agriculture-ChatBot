import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from app.ai.registry import ai_tool_registry
from app.ai.orchestrator.planner import ExecutionPlan, PlanStep

class ToolRegistryMetadata(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any] = {}
    health_status: str = "healthy"
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ToolLogEntry(BaseModel):
    log_id: str
    user_id: str
    tool_name: str
    parameters: Dict[str, Any]
    output: Dict[str, Any] = {}
    execution_time_seconds: float = 0.0
    status: str = "success"  # success, failed, timeout
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ToolRouter:
    """
    Tool Router and Execution Service.
    Configures tool dynamic registration metadata and executes DAG tasks.
    Supports Timeout, Parallelism, Retries, and Timing Metrics logs.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.registry = ai_tool_registry

    async def register_tool_metadata(self, tool_name: str, desc: str, input_fields: Dict[str, Any]) -> None:
        metadata = ToolRegistryMetadata(
            name=tool_name,
            description=desc,
            input_schema=input_fields
        )
        await self.db["tool_registry"].replace_one(
            {"name": tool_name},
            metadata.model_dump(),
            upsert=True
        )

    async def execute_step(
        self,
        step: PlanStep,
        user_id: str,
        timeout: float = 5.0,
        retries: int = 2
    ) -> Dict[str, Any]:
        """
        Executes a single step with validation, timing stats, error handling, and timeout.
        """
        start_time = time.time()
        tool_name = step.tool_name
        params = step.parameters
        
        attempt = 0
        output = {}
        status = "failed"
        
        while attempt <= retries:
            try:
                # Execution with timeout limits
                res = await asyncio.wait_for(
                    self.registry.execute_tool(tool_name, params, user_id),
                    timeout=timeout
                )
                output = res
                status = "success"
                break
            except asyncio.TimeoutError:
                status = "timeout"
                attempt += 1
            except Exception as e:
                status = "failed"
                output = {"error": str(e)}
                attempt += 1

        duration = time.time() - start_time
        
        # Log result
        log_entry = ToolLogEntry(
            log_id=step.step_id,
            user_id=user_id,
            tool_name=tool_name,
            parameters=params,
            output=output,
            execution_time_seconds=round(duration, 3),
            status=status
        )
        
        await self.db["tool_logs"].insert_one(log_entry.model_dump())
        return log_entry.model_dump()

    async def execute_plan(self, plan: ExecutionPlan, user_id: str) -> List[Dict[str, Any]]:
        """
        Executes steps dynamically based on plan mode (sequential or parallel).
        """
        if plan.execution_mode == "parallel":
            # Run all steps concurrently
            tasks = [self.execute_step(step, user_id) for step in plan.steps]
            results = await asyncio.gather(*tasks)
            return results
        else:
            # Sequential execution
            results = []
            for step in plan.steps:
                res = await self.execute_step(step, user_id)
                results.append(res)
            return results
