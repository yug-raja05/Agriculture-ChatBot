import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI Enterprise - DevOps & Backup Verification Check")
print("=========================================")

async def test_enterprise_platform():
    try:
        print("1. Verifying Backup & Recovery execution...")
        from app.core.backup import run_backup, run_restore
        
        # Trigger simulated backup
        run_backup(backup_dest="verify_backups")
        
        # Verify ZIP archive creation
        archives = [f for f in os.listdir("verify_backups") if f.endswith(".zip")]
        print(f"   [OK] Total generated backup archives: {len(archives)}")
        
        # Trigger restore verification
        target_zip = os.path.join("verify_backups", archives[0])
        run_restore(target_zip)
        print("   [OK] Restore executed successfully.")
        
        # Cleanup staging backups folder
        os.remove(target_zip)
        os.rmdir("verify_backups")
        
        print("2. Importing system monitoring services...")
        from app.api.v1.endpoints.enterprise import get_system_monitoring
        print("   [OK] Enterprise monitoring and log viewer modules compiled successfully.")
        
        print("\n[SUCCESS] AI Enterprise Platform passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Enterprise Platform verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_enterprise_platform())
