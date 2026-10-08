import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI Brain - LangChain Verification Check")
print("=========================================")

async def test_agent_pipeline():
    try:
        print("1. Loading LLM Config & Singleton Model Loader...")
        from app.ai.llm import get_llm
        llm = get_llm()
        print(f"   [OK] Loaded LLM Model class: {llm.__class__.__name__}")

        print("2. Verifying Prompt Templates Manager...")
        from app.ai.prompts import prompt_manager
        weather_prompt = prompt_manager.get_prompt_template("weather")
        print(f"   [OK] Weather template keys: {weather_prompt.input_variables}")
        
        print("3. Initializing LangChain Agent Executor...")
        from app.ai.agent_executor import agent_brain
        print(f"   [OK] Agent Brain instance: {agent_brain.__class__.__name__}")
        
        print("4. Testing Async Token Streaming Queue Output...")
        queue = asyncio.Queue()
        dummy_profile = {
            "fullname": "John Doe",
            "location": "Central Valley",
            "farm_size_hectares": 12.5,
            "primary_crops": ["Maize"],
            "soil_profile": {"nitrogen": 45.2, "phosphorus": 22.1, "potassium": 120.5, "ph": 6.8, "moisture": 40.0}
        }
        
        # Launch agent loop task
        task = asyncio.create_task(
            agent_brain.execute_agent_loop(
                query="Will it rain tomorrow?",
                user_id="user_1",
                chat_history=[],
                profile=dummy_profile,
                queue=queue
            )
        )
        
        tokens_received = []
        while not task.done() or not queue.empty():
            try:
                token = await asyncio.wait_for(queue.get(), timeout=0.1)
                tokens_received.append(token)
            except asyncio.TimeoutError:
                continue
                
        res = await task
        print(f"   [OK] Total tokens streamed: {len(tokens_received)}")
        print(f"   [OK] Final content summary: {res['content'][:60]}...")
        
        print("\n[SUCCESS] AI Brain LangChain pipeline passes tests perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Brain verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_agent_pipeline())
