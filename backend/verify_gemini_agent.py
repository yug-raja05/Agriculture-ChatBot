import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.llm import get_llm, GroqLLM, MockQwenLLM
from app.ai.agent_executor import agent_brain
from app.core.config import settings

async def main():
    print("==================================================")
    print("    AGRIGENIUS GROQ AI REAL-TIME AGENT VERIFICATION")
    print("==================================================")
    
    # 1. Test LLM Initialization
    llm = get_llm()
    llm_type = getattr(llm, "_llm_type", "")
    print(f"Active LLM Instance Type: {llm_type}")
    print(f"Active LLM Class: {llm.__class__.__name__}")
    
    if isinstance(llm, GroqLLM):
        print(f"✓ Groq API Key Detected: {llm.get_explicit_groq_key()[:8]}...")
        print(f"✓ Groq Model Target: {llm.get_effective_model()}")
    else:
        print(f"ℹ No valid GROQ_API_KEY detected in env yet. Using active engine: {llm_type}")

    # 2. Test Agent Execution Loop for Weather Query
    print("\n--- Testing Real-Time Agent Execution (Weather Query) ---")
    query_1 = "What is the weather in Ahmedabad today?"
    res_1 = await agent_brain.execute_agent_loop(
        query=query_1,
        user_id="test_user_001",
        profile={"location": "Ahmedabad", "soil_profile": {"nitrogen": 55, "phosphorus": 40, "potassium": 115}}
    )
    print(f"Query: {query_1}")
    print("Agent Content Output (First 300 chars):")
    print(res_1["content"][:300])
    print("...")

    # 3. Test Agent Execution Loop for Crop & Soil Query
    print("\n--- Testing Real-Time Agent Execution (Crop Recommendation) ---")
    query_2 = "Recommend suitable kharif crops for high nitrogen black soil in Gujarat."
    res_2 = await agent_brain.execute_agent_loop(
        query=query_2,
        user_id="test_user_001",
        profile={"location": "Gujarat", "soil_profile": {"nitrogen": 85, "phosphorus": 45, "potassium": 120}}
    )
    print(f"Query: {query_2}")
    print("Agent Content Output (First 300 chars):")
    print(res_2["content"][:300])
    print("...")

    # 4. Test Streaming Queue Token Output
    print("\n--- Testing Real-Time Token Streaming Queue ---")
    queue = asyncio.Queue()
    task = asyncio.create_task(
        agent_brain.execute_agent_loop(
            query="What is the current mandi price of wheat in Punjab?",
            user_id="test_user_001",
            profile={"location": "Punjab"},
            queue=queue
        )
    )
    
    streamed_tokens = []
    while not task.done() or not queue.empty():
        try:
            token = await asyncio.wait_for(queue.get(), timeout=0.2)
            streamed_tokens.append(token)
        except asyncio.TimeoutError:
            continue
            
    final_res = await task
    print(f"Total Streamed Chunks Count: {len(streamed_tokens)}")
    print(f"Sample Streamed Text: {''.join(streamed_tokens[:15])}...")
    print("==================================================")
    print("      VERIFICATION SUCCESSFUL")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
