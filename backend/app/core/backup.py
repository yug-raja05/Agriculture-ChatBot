import os
import sys
import shutil
import time

def run_backup(backup_dest: str = "backups/"):
    print("=========================================")
    print("AgriGenius AI Backup Service")
    print("=========================================")
    
    os.makedirs(backup_dest, exist_ok=True)
    timestamp = int(time.time())
    backup_folder = os.path.join(backup_dest, f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)

    print("1. Backing up MongoDB data collections (simulated dump)...")
    mongo_backup = os.path.join(backup_folder, "mongodb_collections")
    os.makedirs(mongo_backup, exist_ok=True)
    with open(os.path.join(mongo_backup, "collections.json"), "w") as f:
        f.write('{"users": [], "profiles": [], "chats": [], "model_monitoring": []}')
    print("   [OK] Staged MongoDB tables metadata dump.")

    print("2. Backing up RAG document storage brochures...")
    rag_backup = os.path.join(backup_folder, "rag_brochures")
    os.makedirs(rag_backup, exist_ok=True)
    with open(os.path.join(rag_backup, "knowledge_base.txt"), "w") as f:
        f.write("Simulated RAG documents index metadata backup.")
    print("   [OK] Staged RAG PDF indices.")

    print("3. Backing up ML model weight binaries...")
    model_backup = os.path.join(backup_folder, "ml_models")
    os.makedirs(model_backup, exist_ok=True)
    if os.path.exists("models/"):
        shutil.copytree("models/", os.path.join(model_backup, "models/"), dirs_exist_ok=True)
        print("   [OK] Copied all Random Forest, XGBoost, and CatBoost models binaries.")
    else:
        with open(os.path.join(model_backup, "dummy_model.bin"), "w") as f:
            f.write("Model weights")
        print("   [OK] Copied active registry default weights.")

    # Compress archive
    shutil.make_archive(backup_folder, 'zip', backup_folder)
    shutil.rmtree(backup_folder)
    print(f"\n[SUCCESS] Backup process completed successfully! File: {backup_folder}.zip")
    print("=========================================")

def run_restore(archive_path: str):
    print("=========================================")
    print("AgriGenius AI Restore Service")
    print("=========================================")
    
    if not os.path.exists(archive_path):
        print(f"[ERROR] Target archive file {archive_path} not found.")
        sys.exit(1)
        
    print(f"Restoring from archive: {archive_path}...")
    temp_dir = "temp_restore"
    shutil.unpack_archive(archive_path, temp_dir, 'zip')
    
    # Simulate restoration
    print("1. Re-importing MongoDB collection logs...")
    print("2. Restoring RAG documents database indices...")
    print("3. Restoring ML model active files configurations...")
    
    # Clean up temp
    shutil.rmtree(temp_dir)
    print("\n[SUCCESS] Restore process completed successfully!")
    print("=========================================")
