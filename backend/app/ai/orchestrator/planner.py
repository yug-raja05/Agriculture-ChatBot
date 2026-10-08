import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    parameters: Dict[str, Any] = {}
    execution_order: int = 1
    dependency_ids: List[str] = []
    status: str = "pending"

class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    steps: List[PlanStep] = []
    execution_mode: str = "single"  # single, multiple, sequential, parallel
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Planner:
    """
    Agent Execution Planner.
    Calculates execution DAG steps, parallel options, and logs steps.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_plan(
        self,
        user_id: str,
        intents: List[str],
        entities: Dict[str, Any],
        location: str = "Gujarat"
    ) -> ExecutionPlan:
        steps = []
        exec_mode = "single"

        # Determine steps based on intents
        order = 1
        for intent in intents:
            if intent == "Weather Query":
                steps.append(PlanStep(
                    tool_name="weather_advisor",
                    parameters={"location": location, "days_forecast": 3},
                    execution_order=order
                ))
                order += 1
            elif intent == "Disease Query":
                steps.append(PlanStep(
                    tool_name="plant_disease_detector",
                    parameters={"image_url": "uploaded_scan.jpg"},
                    execution_order=order
                ))
                order += 1
            elif intent == "Crop Recommendation":
                steps.append(PlanStep(
                    tool_name="crop_recommender",
                    parameters={"nitrogen": 50.0, "phosphorus": 35.0, "potassium": 110.0, "ph": 6.5, "moisture": 35.0},
                    execution_order=order
                ))
                order += 1
            elif intent == "Market Query":
                steps.append(PlanStep(
                    tool_name="market_price_assistant",
                    parameters={"crop_name": entities.get("crop") or "Wheat"},
                    execution_order=order
                ))
                order += 1
            elif intent == "Government Scheme Query":
                steps.append(PlanStep(
                    tool_name="government_schemes_advisor",
                    parameters={"scheme_name": "PM-KISAN", "state": location},
                    execution_order=order
                ))
                order += 1
            elif intent == "Soil Analysis":
                steps.append(PlanStep(
                    tool_name="fertilizer_advisor",
                    parameters={"crop_name": entities.get("crop") or "Wheat", "soil_type": "Loamy"},
                    execution_order=order
                ))
                order += 1

        if len(steps) > 1:
            # Parallel execution possible for independent queries (e.g. weather + market)
            exec_mode = "parallel"
            # Set all steps execution order to 1 since there are no dependencies
            for step in steps:
                step.execution_order = 1

        plan = ExecutionPlan(
            user_id=user_id,
            steps=steps,
            execution_mode=exec_mode
        )
        
        # Save to database log
        await self.db["planner_logs"].insert_one(plan.model_dump())
        return plan
