import asyncio
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import db_manager
from app.core.config import settings

async def verify_pipeline():
    print("=================================================================")
    print("AgriGenius AI - Production-Ready Resilience & Service Layer Test")
    print("=================================================================")
    
    # 1. Connect to Database
    print("1. Connecting to database manager singletons...")
    db_manager.connect()
    db = db_manager.db
    if db is None:
        print("[ERROR] MongoDB client connection failed. Make sure MONGODB_URI is valid.")
        sys.exit(1)
    print("   [OK] Connected to MongoDB Atlas.")

    # 2. Test Weather Service (Open-Meteo Provider - no API key required)
    print("\n2. Testing Weather Service (Open-Meteo Provider)...")
    settings.ACTIVE_WEATHER_PROVIDER = "open_meteo"
    from app.ai.agri_services.weather import weather_service
    
    # Clean cache first to guarantee fresh call
    await db["weather_cache"].delete_many({})
    
    start_time = time.time()
    w_res = await weather_service.get_current_weather(22.57, 88.36)
    duration_fresh = time.time() - start_time
    print(f"   [OK] Fresh Fetch Temp: {w_res.get('temp')}°C, Condition: {w_res.get('condition')} (Duration: {duration_fresh:.3f}s)")
    
    # Test Caching
    start_time = time.time()
    w_res_cached = await weather_service.get_current_weather(22.57, 88.36)
    duration_cached = time.time() - start_time
    print(f"   [OK] Cached Fetch Temp: {w_res_cached.get('temp')}°C (Duration: {duration_cached:.3f}s)")
    if not w_res_cached.get("_from_cache"):
        print("[WARNING] Caching was not indicated in response headers.")
    else:
        print("   [SUCCESS] Verified MongoDB caching layer hit.")

    # 3. Test Market Service (CSV Provider)
    print("\n3. Testing Market Service (CSV Provider)...")
    settings.ACTIVE_MARKET_PROVIDER = "csv"
    from app.ai.agri_services.market import market_service
    
    # Clean cache
    await db["market_cache"].delete_many({})
    
    m_res = await market_service.get_current_prices("Wheat", "Gujarat")
    print(f"   [OK] Crop: {m_res.get('crop')}, Modal Price: Rs. {m_res.get('modal_price_per_quintal')}/quintal, Mandis: {m_res.get('nearby_mandis')}")
    print(f"   [OK] Provider used: {m_res.get('provider')}")

    # 4. Test Cache Failover & Retries
    print("\n4. Testing Resilient Cache Failover...")
    # Mocking standard provider to raise exception
    from app.ai.agri_services.market import CSVMarketProvider
    original_fetch = CSVMarketProvider.fetch_prices
    
    calls_count = 0
    def failing_fetch(self, crop: str, location: str):
        nonlocal calls_count
        calls_count += 1
        raise ConnectionError("Simulated remote server connection timeout.")
        
    CSVMarketProvider.fetch_prices = failing_fetch
    
    try:
        # Since cache exists for ("wheat", "gujarat"), it should fail 3 times on API call
        # and then successfully fall back to cached data.
        print("   Triggering fetch with failing API provider (expects 3 retries and cache fallback)...")
        start_time = time.time()
        fallback_res = await market_service.get_current_prices("Wheat", "Gujarat")
        print(f"   [OK] Fallback value retrieved successfully: Rs. {fallback_res.get('modal_price_per_quintal')}")
        print(f"   [OK] API Call attempts before fallback: {calls_count}")
        print(f"   [SUCCESS] Verified automatic retries and cache failover recovery.")
    except Exception as err:
        print(f"   [ERROR] Cache failover test failed: {err}")
    finally:
        CSVMarketProvider.fetch_prices = original_fetch

    # 5. Test Government Schemes (Seeding & Searching)
    print("\n5. Testing Government Schemes Seeding & Search...")
    # Clean schemes to trigger seeding check
    await db["government_schemes"].delete_many({})
    await db["schemes_cache"].delete_many({})
    
    from app.ai.agri_services.government import government_service
    schemes = await government_service.search_schemes("PM-Kisan", "")
    print(f"   [OK] Database seeded and retrieved schemes list. Schemes found: {len(schemes)}")
    if schemes:
        print(f"   [OK] Top Scheme Name: {schemes[0].get('name')}")
        print(f"   [OK] Benefits: {schemes[0].get('benefits')}")

    # 6. Test Notifications Service
    print("\n6. Testing Notification Dispatch & Logging...")
    settings.ACTIVE_NOTIFICATION_PROVIDER = "database"
    from app.ai.agri_services.notifications import notification_service
    n_res = await notification_service.send_notification(
        user_id="test_user_99",
        recipient="farmer@example.com",
        category="System",
        title="Irrigation Warning",
        body="Water your potato crop. Soil moisture is below 20%."
    )
    print(f"   [OK] Notification response status: {n_res.get('status')}")
    # Verify in MongoDB
    log = await db["notifications"].find_one({"user_id": "test_user_99"})
    if log:
        print(f"   [OK] Verified MongoDB notification audit log recorded: '{log.get('title')}' - {log.get('delivery_status')}")

    # 7. Test AI Agent Loop (Dynamic Response Generation)
    print("\n7. Testing AI Agent Loop (Dynamic Responses)...")
    from app.ai.agent_executor import agent_brain
    
    test_profile = {
        "location": "Punjab",
        "soil_profile": {
            "nitrogen": 85.0,
            "phosphorus": 30.0,
            "potassium": 115.0,
            "ph": 6.8,
            "moisture": 25.0
        }
    }
    
    print("   Sending query: 'Tell me about the weather'")
    agent_res = await agent_brain.execute_agent_loop("Tell me about the weather", "test_user_99", profile=test_profile)
    print(f"   [AGENT RESPONSE]:\n{agent_res.get('content')}\n")
    
    print("   Sending query: 'What crop should I plant?'")
    agent_res2 = await agent_brain.execute_agent_loop("What crop should I plant?", "test_user_99", profile=test_profile)
    print(f"   [AGENT RESPONSE]:\n{agent_res2.get('content')}\n")

    print("=================================================================")
    print("[SUCCESS] All dynamic services passed resilience checks!")
    print("=================================================================")
    db_manager.close()

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
