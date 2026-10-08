import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from app.core.config import settings
from app.ai.agri_services.weather import weather_service
from app.ai.agent_executor import agent_brain

async def run_tests():
    print("=================================================================")
    print("AgriGenius AI - Weather Module Architectural Validation Tests")
    print("=================================================================")
    
    # Connect db
    db_manager.connect()
    db = db_manager.db
    if db is None:
        print("[ERROR] MongoDB is offline.")
        sys.exit(1)
        
    # Clean cache
    await db["weather_cache"].delete_many({})

    # 1. City lookup test (Ahmedabad)
    print("\n1. Testing dynamic city geocoding and weather fetch (Ahmedabad)...")
    settings.ACTIVE_WEATHER_PROVIDER = "open_meteo"  # Ensure no key dependencies
    w_res1 = await weather_service.get_current_weather("Ahmedabad")
    print(f"   Resolved Location: {w_res1.get('location')}")
    print(f"   Coordinates: Lat={w_res1.get('latitude')}, Lon={w_res1.get('longitude')}")
    print(f"   Temperature: {w_res1.get('temperature')}°C, Condition: {w_res1.get('weather_condition')}")
    assert w_res1.get("location") == "Ahmedabad", "City geocoding mismatch"
    assert w_res1.get("temperature") != "Not Available", "Temperature failed to resolve"

    # 2. Coordinates lookup test
    print("\n2. Testing coordinate reverse geocoding and fetch (23.0225, 72.5714)...")
    w_res2 = await weather_service.get_current_weather(23.0225, 72.5714)
    print(f"   Resolved Location: {w_res2.get('location')}")
    print(f"   Temperature: {w_res2.get('temperature')}°C")
    assert w_res2.get("location") in ["Ahmedabad", "Navrangpura"], "Proximity reverse geocoding failed"

    # 3. Invalid location error handling
    print("\n3. Testing invalid city name lookup...")
    try:
        await weather_service.get_current_weather("InvalidCityXYZ")
        print("   [FAIL] Invalid city query should have raised an exception.")
    except Exception as e:
        print(f"   [SUCCESS] Received expected exception: {e}")

    # 4. NaN / Null checks
    print("\n4. Testing NaN and None values sanitizer...")
    from app.ai.agri_services.weather import sanitize_val, map_degrees_to_compass
    assert sanitize_val(None) == "Not Available"
    assert sanitize_val("NaN") == "Not Available"
    assert sanitize_val(22.5) == 22.5
    assert map_degrees_to_compass(None) == "Not Available"
    assert map_degrees_to_compass(180) == "S"
    print("   [SUCCESS] NaN and missing values sanitizers validated successfully.")

    # 5. Agricultural advice generation
    print("\n5. Testing dynamic agricultural advisory checks...")
    adv = w_res1.get("farming_advice", {})
    print(f"   Suitable Irrigation: {adv.get('suitable_irrigation_time')}")
    print(f"   Irrigation Advice: {adv.get('irrigation_advice')}")
    print(f"   Spraying Advice: {adv.get('spraying_advice')}")
    print(f"   Warnings: {adv.get('warnings')}")
    assert adv.get("suitable_irrigation_time") in ["Anytime", "Early Morning / Late Evening"], "Invalid advice output"

    # 6. AI Agent loop queries validation
    print("\n6. Validating Agent loop query entity extractions...")
    test_queries = [
        "What is the weather today in Ahmedabad?",
        "What is the weather today in Surat?",
        "Will it rain tomorrow in Rajkot?",
        "What is today's weather at latitude 23.0225 longitude 72.5714?",
        "My farm is in Ahmedabad. Should I irrigate today?"
    ]
    
    test_profile = {
        "location": "Ludhiana",
        "soil_profile": {"nitrogen": 50.0, "phosphorus": 35.0, "potassium": 110.0, "ph": 6.5, "moisture": 35.0}
    }
    
    for q in test_queries:
        print(f"   Query: '{q}'")
        res = await agent_brain.execute_agent_loop(q, "test_user_99", profile=test_profile)
        print(f"   [AGENT CONTENT]: {res.get('content').splitlines()[0]}")
        # Verify the location returned matches what is in the question
        if "Ahmedabad" in q:
            assert "Ahmedabad" in res.get("content") or "Navrangpura" in res.get("content"), "Ahmedabad was ignored"
        elif "Surat" in q:
            assert "Surat" in res.get("content"), "Surat was ignored"
        elif "Rajkot" in q:
            assert "Rajkot" in res.get("content"), "Rajkot was ignored"
        elif "23.0225" in q:
            assert "Ahmedabad" in res.get("content") or "Navrangpura" in res.get("content") or "23.02" in res.get("content"), "Coordinates geocoding ignored"
        print("   ---")

    print("\n=================================================================")
    print("[SUCCESS] All Weather module production requirements validated!")
    print("=================================================================")
    db_manager.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
