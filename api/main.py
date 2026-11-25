from typing import Optional, List
from decimal import Decimal
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings

DASHBOARD_FILE = Path(__file__).resolve().parent.parent / "outputs" / "dashboard.html"
STORE_FILE = Path(__file__).resolve().parent.parent / "data" / "properties_store.json"

app = FastAPI(
    title="US Real Estate Intelligence REST API",
    description="Custom Enterprise API serving Residential (Zillow), Commercial (LoopNet), and Land Parcel (LandGlide) data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_record(d: dict) -> dict:
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
        connect_timeout=2,
        cursor_factory=RealDictCursor
    )

def get_bundled_properties() -> list[dict]:
    """Fallback when running on cloud serverless without remote database configured"""
    if STORE_FILE.exists():
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            records = list(data.values())
            for idx, r in enumerate(records, 1):
                if not r.get("id"):
                    r["id"] = idx
            return records
        except Exception:
            return []
    return []

@app.get("/", response_class=HTMLResponse, tags=["Frontend UI"])
def get_root_ui():
    if DASHBOARD_FILE.exists():
        return FileResponse(DASHBOARD_FILE)
    return "<h1>Dashboard UI file not found</h1>"

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend UI"])
def get_dashboard_ui():
    return FileResponse(DASHBOARD_FILE)

@app.get("/api/v1/health", tags=["System"])
def health_check():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return {"status": "healthy", "database": "PostgreSQL 16", "mode": "database"}
    except Exception:
        return {"status": "healthy", "database": "bundled_store", "mode": "serverless_fallback"}

@app.get("/api/v1/stats", tags=["Analytics & KPIs"])
def get_analytics_stats():
    try:
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
    except Exception:
        records = get_bundled_properties()
        sources = {}
        states = {}
        prices = []
        for r in records:
            s = r.get("source", "unknown")
            sources[s] = sources.get(s, 0) + 1
            st = r.get("state", "US")
            states[st] = states.get(st, 0) + 1
            if r.get("price") is not None:
                prices.append(float(r["price"]))

        avg_p = round(sum(prices) / len(prices), 2) if prices else 0.0
        max_p = max(prices) if prices else 0.0
        tot_v = round(sum(prices), 2) if prices else 0.0

        return {
            "total_properties": len(records),
            "sources_breakdown": sorted([{"source": k, "count": v} for k, v in sources.items()], key=lambda x: x["count"], reverse=True),
            "states_breakdown": sorted([{"state": k, "count": v} for k, v in states.items()], key=lambda x: x["count"], reverse=True),
            "financial_summary": {"avg_price": avg_p, "max_price": max_p, "total_volume": tot_v}
        }

@app.get("/api/v1/properties", tags=["Properties"])
def list_properties(
    search: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    try:
        query = "SELECT * FROM properties WHERE 1=1"
        params = []

        if search:
            query += " AND (title ILIKE %s OR address ILIKE %s OR city ILIKE %s OR owner_name ILIKE %s OR external_id ILIKE %s)"
            term = f"%{search}%"
            params.extend([term, term, term, term, term])

        if source:
            if source == "us_parcels":
                query += " AND source IN ('texas_cad', 'landglide', 'us_parcels')"
            else:
                query += " AND source = %s"
                params.append(source)

        if state and state.lower() != "all":
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

        return {"total": total_matching, "limit": limit, "offset": offset, "results": items}

    except Exception:
        # Fallback to bundled data
        records = get_bundled_properties()
        filtered = []
        for r in records:
            if source and source.lower() != "all":
                if source == "us_parcels" and r.get("source") not in ["texas_cad", "landglide", "us_parcels"]:
                    continue
                elif source != "us_parcels" and r.get("source") != source:
                    continue

            if state and state.lower() != "all" and r.get("state") != state.upper():
                continue

            if city and city.lower() not in (r.get("city") or "").lower():
                continue

            if property_type and property_type.lower() not in (r.get("property_type") or "").lower():
                continue

            if min_price is not None and (r.get("price") is None or float(r["price"]) < min_price):
                continue

            if max_price is not None and (r.get("price") is None or float(r["price"]) > max_price):
                continue

            if search:
                s = search.lower()
                m = f"{r.get('title','')} {r.get('address','')} {r.get('city','')} {r.get('owner_name','')} {r.get('external_id','')}".lower()
                if s not in m:
                    continue

            filtered.append(r)

        return {"total": len(filtered), "limit": limit, "offset": offset, "results": filtered[offset:offset+limit]}

@app.get("/api/v1/properties/{property_id}", tags=["Properties"])
def get_property_detail(property_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM properties WHERE id = %s;", (property_id,))
                prop = cur.fetchone()
                if prop:
                    cur.execute("SELECT * FROM price_history WHERE property_id = %s ORDER BY changed_at DESC;", (property_id,))
                    price_history = [clean_record(r) for r in cur.fetchall()]
                    prop = clean_record(prop)
                    prop["price_history"] = price_history
                    return prop
    except Exception:
        pass

    records = get_bundled_properties()
    for r in records:
        if r.get("id") == property_id:
            r["price_history"] = []
            return r

    raise HTTPException(status_code=404, detail="Property not found")

@app.get("/api/v1/zillow", tags=["Platform APIs"])
def get_zillow_listings(city: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
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
    except Exception:
        records = [r for r in get_bundled_properties() if r.get("source") == "zillow"]
        if city:
            records = [r for r in records if city.lower() in (r.get("city") or "").lower()]
        if state:
            records = [r for r in records if (r.get("state") or "").upper() == state.upper()]
        return {"count": len(records), "results": records[offset:offset+limit]}

@app.get("/api/v1/loopnet", tags=["Platform APIs"])
def get_loopnet_listings(property_type: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
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
    except Exception:
        records = [r for r in get_bundled_properties() if r.get("source") == "loopnet"]
        if property_type:
            records = [r for r in records if property_type.lower() in (r.get("property_type") or "").lower()]
        if city:
            records = [r for r in records if city.lower() in (r.get("city") or "").lower()]
        if state:
            records = [r for r in records if (r.get("state") or "").upper() == state.upper()]
        return {"count": len(records), "results": records[offset:offset+limit]}

@app.get("/api/v1/landglide", tags=["Platform APIs"])
def get_landglide_parcels(county: Optional[str] = None, owner_name: Optional[str] = None, state: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
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
    except Exception:
        records = [r for r in get_bundled_properties() if r.get("source") in ["landglide", "texas_cad", "us_parcels"]]
        if county:
            records = [r for r in records if county.lower() in (r.get("county") or "").lower()]
        if owner_name:
            records = [r for r in records if owner_name.lower() in (r.get("owner_name") or "").lower()]
        if state:
            records = [r for r in records if (r.get("state") or "").upper() == state.upper()]
        return {"count": len(records), "results": records[offset:offset+limit]}

@app.get("/api/v1/regrid", tags=["Platform APIs"])
def get_regrid_parcels(
    county: Optional[str] = None,
    owner_name: Optional[str] = None,
    state: Optional[str] = None,
    zoning: Optional[str] = None,
    min_acres: Optional[float] = None,
    max_acres: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Search and retrieve Regrid (regrid.com) nationwide parcel data,
    including APN, owner details, tax valuations, GIS acreage, zoning,
    and GeoJSON boundary polygon coordinates.
    """
    try:
        query = "SELECT * FROM regrid_parcels WHERE 1=1"
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
        if zoning:
            query += " AND zoning ILIKE %s"
            params.append(f"%{zoning}%")
        if min_acres is not None:
            query += " AND lot_acres >= %s"
            params.append(min_acres)
        if max_acres is not None:
            query += " AND lot_acres <= %s"
            params.append(max_acres)

        query += " ORDER BY lot_acres DESC NULLS LAST LIMIT %s OFFSET %s;"
        params.extend([limit, offset])
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                items = [clean_record(r) for r in cur.fetchall()]
        return {"count": len(items), "platform": "regrid.com", "results": items}
    except Exception:
        records = [r for r in get_bundled_properties() if r.get("source") == "regrid"]
        if county:
            records = [r for r in records if county.lower() in (r.get("county") or "").lower()]
        if owner_name:
            records = [r for r in records if owner_name.lower() in (r.get("owner_name") or "").lower()]
        if state:
            records = [r for r in records if (r.get("state") or "").upper() == state.upper()]
        if zoning:
            records = [r for r in records if zoning.lower() in (r.get("zoning") or "").lower()]
        if min_acres is not None:
            records = [r for r in records if (r.get("lot_size_acres") or 0) >= min_acres]
        if max_acres is not None:
            records = [r for r in records if (r.get("lot_size_acres") or 0) <= max_acres]
        return {"count": len(records), "platform": "regrid.com", "results": records[offset:offset+limit]}

@app.get("/api/v1/geojson", tags=["Spatial GIS"])
def get_geojson_features(
    source: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000)
):
    """Returns a standard GeoJSON FeatureCollection (Polygon boundaries for parcels, Points for listings)."""
    rows = []
    try:
        query = "SELECT id, source, external_id, title, property_type, price, tax_assessed_value, lot_size_acres, address, city, county, state, parcel_id, owner_name, zoning, latitude, longitude, raw_data FROM properties WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        params = []
        if source and source.lower() != "all":
            if source == "us_parcels":
                query += " AND source IN ('texas_cad', 'landglide', 'us_parcels')"
            else:
                query += " AND source = %s"
                params.append(source)
        if state and state.lower() != "all":
            query += " AND state = %s"
            params.append(state.upper())
        query += " LIMIT %s;"
        params.append(limit)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = [clean_record(r) for r in cur.fetchall()]
    except Exception:
        for r in get_bundled_properties():
            if r.get("latitude") is None or r.get("longitude") is None:
                continue
            if source and source.lower() != "all":
                if source == "us_parcels" and r.get("source") not in ["texas_cad", "landglide", "us_parcels"]:
                    continue
                elif source != "us_parcels" and r.get("source") != source:
                    continue
            if state and state.lower() != "all" and r.get("state") != state.upper():
                continue
            rows.append(r)
            if len(rows) >= limit:
                break

    features = []
    for r in rows:
        raw = r.get("raw_data") if isinstance(r.get("raw_data"), dict) else {}
        geom = raw.get("geojson_geometry") or {
            "type": "Point",
            "coordinates": [float(r["longitude"]), float(r["latitude"])]
        }
        features.append({
            "type": "Feature",
            "id": r.get("id"),
            "geometry": geom,
            "properties": {
                "id": r.get("id"),
                "source": r.get("source"),
                "external_id": r.get("external_id"),
                "title": r.get("title"),
                "address": r.get("address"),
                "city": r.get("city"),
                "county": r.get("county"),
                "state": r.get("state"),
                "price": r.get("price"),
                "tax_assessed_value": r.get("tax_assessed_value"),
                "lot_size_acres": r.get("lot_size_acres"),
                "owner_name": r.get("owner_name"),
                "zoning": r.get("zoning")
            }
        })
    return {"type": "FeatureCollection", "count": len(features), "features": features}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
