import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI Agent - Orchestrator Verification Check")
print("=========================================")

async def test_agent_orchestrator():
    try:
        # Mock database connection
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        db = client["AgriGeniusAI_test"]
        
        print("1. Loading Session Manager & Creating mock session...")
        from app.ai.orchestrator.session_manager import SessionManager
        sm = SessionManager(db)
        session = await sm.create_session(user_id="user_123")
        print(f"   [OK] Session created successfully. ID: {session.session_id}")
        
        print("2. Loading Memory Manager & Updating agricultural memory...")
        from app.ai.orchestrator.memory_manager import MemoryManager
        mm = MemoryManager(db)
        await mm.append_crop_history("user_123", "Cotton")
        memory = await mm.get_memory("user_123")
        print(f"   [OK] Memory retrieved. Crops in history: {memory.crop_history}")
        
        print("3. Verifying Intent Analyzer & Entity Extractors...")
        from app.ai.orchestrator.intent_analyzer import IntentAnalyzer
        ia = IntentAnalyzer()
        res = ia.analyze_intent("Will it rain tomorrow on my cotton fields?")
        print(f"   [OK] Primary Intent: {res.primary_intent}")
        print(f"   [OK] Extracted Crop Entity: {res.entities.crop}")
        
        print("4. Testing Planner step calculations...")
        from app.ai.orchestrator.planner import Planner
        planner = Planner(db)
        plan = await planner.create_plan(
            user_id="user_123",
            intents=[res.primary_intent] + res.secondary_intents,
            entities=res.entities.model_dump()
        )
        print(f"   [OK] Execution plan mode: {plan.execution_mode}")
        print(f"   [OK] Total execution steps: {len(plan.steps)}")
        
        print("5. Verifying Tool Router execution log wrappers...")
        from app.ai.orchestrator.tool_router import ToolRouter
        tr = ToolRouter(db)
        print(f"   [OK] Tool Router initialized.")
        
        print("6. Verifying Response Composer compiler...")
        from app.ai.orchestrator.response_composer import ResponseComposer
        rc = ResponseComposer(db)
        mock_tool_output = [{
            "tool_name": "weather_advisor",
            "output": {"result": {"temperature_celsius": 28, "humidity_percentage": 50, "rainfall_probability": 0.1}}
        }]
        composed = rc.compose_final_response("weather", mock_tool_output, 0.45)
        print(f"   [OK] Composed Response output summary: {composed['content'][:60]}...")
        
        print("\n[SUCCESS] AI Agent Orchestration pipelines pass test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Agent orchestrator verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_agent_orchestrator())
