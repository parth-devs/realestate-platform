from typing import Optional, List
from decimal import Decimal
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings

DASHBOARD_FILE = Path(__file__).resolve().parent.parent / "outputs" / "dashboard.html"

app = FastAPI(
    title="US Real Estate Intelligence REST API",
    description="Custom Enterprise API serving Residential (Zillow), Commercial (LoopNet), and Land Parcel (LandGlide) data from PostgreSQL.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", response_class=HTMLResponse, tags=["Frontend UI"])
def get_root_ui():
    """Serves the interactive Real Estate Intelligence Platform Web UI"""
    if DASHBOARD_FILE.exists():
        return FileResponse(DASHBOARD_FILE)
    return "<h1>Dashboard UI file not found</h1>"

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend UI"])
def get_dashboard_ui():
    """Alternative route for the interactive Web UI"""
    return FileResponse(DASHBOARD_FILE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_record(d: dict) -> dict:
    """Recursively converts Decimal and non-serializable objects to float/str"""
    out = {}
    for k, v in d.items():
        if isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, dict):
            out[k] = clean_record(v)
        else:
            out[k] = v
    return out

def get_db_connection():
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

@app.get("/api/v1/health", tags=["System"])
def health_check():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return {"status": "healthy", "database": "connected", "engine": "PostgreSQL 16", "api": "Real Estate Core v1"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@app.get("/api/v1/stats", tags=["Analytics & KPIs"])
def get_analytics_stats():
    """Returns high-level statistics across all US states and platforms"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM properties;")
            total_properties = cur.fetchone()["total"]

            cur.execute("SELECT source, COUNT(*) AS count FROM properties GROUP BY source ORDER BY count DESC;")
            by_source = [clean_record(r) for r in cur.fetchall()]

            cur.execute("SELECT state, COUNT(*) AS count FROM properties GROUP BY state ORDER BY count DESC;")
            by_state = [clean_record(r) for r in cur.fetchall()]

            cur.execute("SELECT AVG(price) AS avg_price, MAX(price) AS max_price, SUM(price) AS total_volume FROM properties WHERE price IS NOT NULL;")
            financials = clean_record(cur.fetchone())

    return {
        "total_properties": total_properties,
        "sources_breakdown": by_source,
        "states_breakdown": by_state,
        "financial_summary": financials
    }

@app.get("/api/v1/properties", tags=["Properties"])
def list_properties(
    search: Optional[str] = Query(None, description="Search by address, city, owner name, or title"),
    source: Optional[str] = Query(None, description="Filter by source: zillow, loopnet, us_parcels, texas_cad"),
    state: Optional[str] = Query(None, description="2-letter US State code (e.g. TX, NY, CA, FL)"),
    city: Optional[str] = Query(None, description="City name"),
    property_type: Optional[str] = Query(None, description="Property type"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Query properties with filtering, full-text search, and pagination"""
    query = "SELECT * FROM properties WHERE 1=1"
    params = []

    if search:
        query += " AND (title ILIKE %s OR address ILIKE %s OR city ILIKE %s OR owner_name ILIKE %s OR external_id ILIKE %s)"
        term = f"%{search}%"
        params.extend([term, term, term, term, term])

    if source:
        query += " AND source = %s"
        params.append(source)

    if state:
        query += " AND state = %s"
        params.append(state.upper())

    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")

    if property_type:
        query += " AND property_type ILIKE %s"
        params.append(f"%{property_type}%")

    if min_price is not None:
        query += " AND price >= %s"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)

    count_query = query.replace("SELECT * FROM", "SELECT COUNT(*) FROM")
    query += " ORDER BY id DESC LIMIT %s OFFSET %s;"
    params_with_paging = params + [limit, offset]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(count_query, params)
            total_matching = cur.fetchone()["count"]

            cur.execute(query, params_with_paging)
            items = [clean_record(r) for r in cur.fetchall()]

    return {
        "total": total_matching,
        "limit": limit,
        "offset": offset,
        "results": items
    }

@app.get("/api/v1/properties/{property_id}", tags=["Properties"])
def get_property_detail(property_id: int):
    """Retrieve full specifications and price history for a single property"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM properties WHERE id = %s;", (property_id,))
            prop = cur.fetchone()
            if not prop:
                raise HTTPException(status_code=404, detail="Property not found")

            cur.execute("SELECT * FROM price_history WHERE property_id = %s ORDER BY changed_at DESC;", (property_id,))
            price_history = [clean_record(r) for r in cur.fetchall()]

    prop = clean_record(prop)
    prop["price_history"] = price_history
    return prop

@app.get("/api/v1/zillow", tags=["Platform APIs"])
def get_zillow_listings(city: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    query = "SELECT * FROM zillow_residential WHERE 1=1"
    params = []
    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")
    if state:
        query += " AND state = %s"
        params.append(state.upper())

    query += " ORDER BY price DESC NULLS LAST LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            items = [clean_record(r) for r in cur.fetchall()]

    return {"count": len(items), "results": items}

@app.get("/api/v1/loopnet", tags=["Platform APIs"])
def get_loopnet_listings(property_type: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    query = "SELECT * FROM loopnet_commercial WHERE 1=1"
    params = []
    if property_type:
        query += " AND property_type ILIKE %s"
        params.append(f"%{property_type}%")
    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")
    if state:
        query += " AND state = %s"
        params.append(state.upper())

    query += " ORDER BY price DESC NULLS LAST LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            items = [clean_record(r) for r in cur.fetchall()]

    return {"count": len(items), "results": items}

@app.get("/api/v1/landglide", tags=["Platform APIs"])
def get_landglide_parcels(county: Optional[str] = None, owner_name: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    query = "SELECT * FROM landglide_parcels WHERE 1=1"
    params = []
    if county:
        query += " AND county ILIKE %s"
        params.append(f"%{county}%")
    if owner_name:
        query += " AND owner_name ILIKE %s"
        params.append(f"%{owner_name}%")
    if state:
        query += " AND state = %s"
        params.append(state.upper())

    query += " ORDER BY lot_acres DESC NULLS LAST LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            items = [clean_record(r) for r in cur.fetchall()]

    return {"count": len(items), "results": items}

def run_async_crawl(city: str, state: str):
    from main import run_pipeline
    run_pipeline(sources=["zillow", "loopnet", "us_parcels"], markets=[{"city": city, "state": state}])

@app.post("/api/v1/crawl/trigger", tags=["Crawl Automation"])
def trigger_crawl(city: str, state: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_async_crawl, city, state)
    return {
        "status": "started",
        "message": f"Crawl job scheduled for {city}, {state} in background.",
        "target": f"{city}, {state}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
