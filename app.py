
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "workflows.json"

app = FastAPI(title="n8n Workflow Popularity API", version="1.0")


def load_workflows():
    if not DATA_FILE.exists():
        raise HTTPException(status_code=500, detail=f"Data file not found: {DATA_FILE}")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read data file: {e}")
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Data file format invalid (expected a list)")
    return data


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


@app.get("/workflows")
def get_workflows(
    platform: Optional[str] = Query(None, description="YouTube, Forum, Google"),
    country: Optional[str] = Query(None, description="US or IN"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("none", description="none or 'views' or 'avg_interest_last_60_days' or 'score'"),
    order: str = Query("desc", description="'asc' or 'desc'"),
):
    items = load_workflows()

    # Filters
    if platform:
        items = [i for i in items if i.get("platform","").lower() == platform.lower()]
    if country:
        items = [i for i in items if i.get("country","").lower() == country.lower()]

    # Sorting (best-effort)
    if sort_by and sort_by != "none":
        def get_sort_key(it):
            pm = it.get("popularity_metrics", {}) or {}
            if sort_by == "views":
                return float(pm.get("views", 0) or 0)
            if sort_by in ("avg_interest", "avg_interest_last_60_days"):
                return float(pm.get("avg_interest_last_60_days", 0) or 0)
            if sort_by == "score":
                return float(it.get("score", 0) or 0)
            # fallback: try direct metric name inside popularity_metrics
            return float(pm.get(sort_by, 0) or 0)
        reverse = True if order == "desc" else False
        items = sorted(items, key=get_sort_key, reverse=reverse)

    total_available = len(items)
    items = items[offset: offset + limit]

    return {"count": len(items), "total_available": total_available, "results": items}
