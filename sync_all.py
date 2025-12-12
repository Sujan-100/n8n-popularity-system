import shutil
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "workflows.json"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def do_sync():
    #Validate JSON loads and is a list
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("ERROR: workflows.json must be a JSON list (array). Aborting.")
            return 1
    except Exception as exc:
        print("ERROR: failed to load workflows.json:", exc)
        return 2

    #Backup current file with timestamp
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = BACKUP_DIR / f"workflows_{now}.json"
    shutil.copy2(DATA_FILE, backup_path)
    print(f"Backed up workflows.json to: {backup_path}")

    #Write meta file
    meta = {"last_synced_utc": now, "item_count": len(data)}
    meta_file = DATA_DIR / "sync_meta.json"
    with open(meta_file, "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Wrote sync_meta.json -> {meta_file}")

    print("Sync completed successfully.")
    return 0

if __name__ == "__main__":
    exit(do_sync())
