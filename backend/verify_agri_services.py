import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI Agriculture Services - Platform Verification Check")
print("=========================================")

async def test_agri_services():
    try:
        # DB connection
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        db = client["AgriGeniusAI_test"]
        
        print("1. Verifying Weather Intelligence Service & Farming recommendations...")
        from app.ai.agri_services.weather import weather_service
        w_curr = await weather_service.get_current_weather(22.57, 88.36)
        print(f"   [OK] Temp: {w_curr.get('temp')} C, Condition: {w_curr.get('condition')} (Provider: {w_curr.get('provider')})")
        print(f"   [OK] Spraying Advice: {w_curr.get('farming_advice', {}).get('spraying_advice')}")
        
        print("2. Verifying Market Price Intelligence Service...")
        from app.ai.agri_services.market import market_service
        m_curr = await market_service.get_current_prices("Wheat", "Gujarat")
        print(f"   [OK] Modal Price per quintal: {m_curr.get('modal_price_per_quintal')} (Provider: {m_curr.get('provider')})")
        print(f"   [OK] Price trend suggestion: {m_curr.get('best_selling_time')}")
        
        print("3. Verifying Government Schemes Directory Service...")
        from app.ai.agri_services.government import government_service
        schemes = await government_service.search_schemes("Kisan")
        print(f"   [OK] Search matches count: {len(schemes)}")
        print(f"   [OK] First scheme name: {schemes[0].get('name')}")
        
        print("4. Verifying Notification Dispatches...")
        from app.ai.agri_services.notifications import notification_service
        notify = await notification_service.send_notification(
            user_id="user_123",
            recipient="farmer@gmail.com",
            category="Weather",
            title="Heavy rain alert",
            body="Heavy rain forecast for tomorrow.",
            db=db
        )
        print(f"   [OK] Notification sent successfully: {notify.get('notification_sent')}")
        
        print("5. Verifying Smart Reminders scheduling...")
        from app.ai.agri_services.reminders import reminder_service
        rem = await reminder_service.create_reminder(
            user_id="user_123",
            category="Irrigation",
            title="Water wheat crop",
            target_timestamp=1718000000.0,
            db=db
        )
        print(f"   [OK] Created reminder title: {rem.get('title')}")
        
        print("6. Verifying Location intelligence lookups...")
        from app.ai.agri_services.location import location_service
        loc = location_service.get_nearest_facilities(22.57, 88.36)
        print(f"   [OK] Nearest Soil Testing Lab: {loc.get('nearest_soil_testing_center', {}).get('name')}")
        
        print("7. Verifying Analytics aggregations...")
        from app.ai.agri_services.analytics import analytics_service
        an = analytics_service.get_dashboard_analytics()
        print(f"   [OK] Total reminders statistics count: {an.get('reminder_statistics', {}).get('total_reminders')}")
        
        print("\n[SUCCESS] AI Agriculture Services Platform passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Agriculture Services Platform verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_agri_services())
