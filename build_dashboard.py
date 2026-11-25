import json
from pathlib import Path
import psycopg2
from config import settings

def normalize_category(prop_type: str | None) -> str:
    if not prop_type:
        return "Residential"
    pt = prop_type.lower()
    if "lot" in pt or "land" in pt or "vacant" in pt or "ag" in pt or "parcel" in pt:
        return "Land & Vacant"
    if "industrial" in pt or "warehouse" in pt:
        return "Industrial"
    if "multi" in pt or "apartment" in pt:
        return "Multi-Family"
    if "commercial" in pt or "office" in pt or "retail" in pt or "flex" in pt or "medical" in pt:
        return "Commercial"
    return "Residential"

def generate_web_dashboard():
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, external_id, title, property_type, listing_status,
                   price, price_per_sqft, lease_rate, tax_assessed_value,
                   beds, baths, sqft, lot_size_acres, year_built,
                   address, city, county, state, zip_code, latitude, longitude,
                   parcel_id, owner_name, legal_description, zoning, broker_name,
                   raw_data
            FROM properties
            ORDER BY state, price DESC NULLS LAST;
        """)
        cols = [d[0] for d in cur.description]
        raw_rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()

    keep_raw_keys = {
        "ll_uuid", "fips", "owner_mailing", "use_code",
        "land_value", "improvement_value", "tax_amount", "tax_year",
        "last_sale_date", "last_sale_price", "geojson_geometry",
        "zestimate", "cap_rate", "exemptions"
    }

    rows = []
    for r in raw_rows:
        cleaned = {}
        for k, v in r.items():
            if v is None:
                continue
            if k == "raw_data" and isinstance(v, dict):
                compact_raw = {rk: rv for rk, rv in v.items() if rk in keep_raw_keys and rv is not None}
                if compact_raw:
                    cleaned["raw_data"] = compact_raw
            elif hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
                cleaned[k] = float(v)
            else:
                cleaned[k] = v
        # Add unified real-estate category and sanitize external source branding from display text
        cleaned["category"] = normalize_category(cleaned.get("property_type"))
        if isinstance(cleaned.get("title"), str):
            cleaned["title"] = (
                cleaned["title"]
                .replace("Regrid Parcel #", "Parcel #")
                .replace("Zillow", "Residential")
                .replace("LoopNet", "Commercial")
                .replace("LandGlide", "Parcel")
            )
        if isinstance(cleaned.get("legal_description"), str):
            cleaned["legal_description"] = cleaned["legal_description"].replace("REGRID", "CAD")
        if isinstance(cleaned.get("broker_name"), str):
            bn = cleaned["broker_name"]
            if "regrid" in bn.lower() or "landglide" in bn.lower():
                cleaned["broker_name"] = "County Tax & GIS Assessor"
        rows.append(cleaned)

    total_count = len(rows)
    compact_json = json.dumps(rows, separators=(",", ":"))

    html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ParcelScope US — Nationwide Property & Land Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <style>
        :root {
            --bg-dark: #090e1a;
            --bg-panel: rgba(15, 23, 42, 0.94);
            --bg-card: #111827;
            --bg-input: #070b14;
            --border: rgba(148, 163, 184, 0.18);
            --border-active: rgba(56, 189, 248, 0.5);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-teal: #14b8a6;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-violet: #a78bfa;
            --accent-pink: #ff2a7a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }

        /* Top Bar (Clean Unified Chrome) */
        .topbar {
            height: 54px;
            background: rgba(9, 14, 26, 0.97);
            border-bottom: 1px solid var(--border);
            padding: 0 16px;
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 12px;
            z-index: 1300;
            flex-shrink: 0;
        }

        .brand-wrap { display: flex; align-items: center; gap: 10px; }
        .brand { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 1rem; letter-spacing: -0.02em; color: #fff; }
        .brand-icon {
            width: 30px; height: 30px; border-radius: 8px;
            background: linear-gradient(135deg, #0d9488, #0284c7);
            display: grid; place-items: center; font-size: 0.95rem;
        }
        .status-pill {
            font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px;
            background: rgba(52, 211, 153, 0.12); color: var(--accent-emerald);
            border: 1px solid rgba(52, 211, 153, 0.28); display: flex; align-items: center; gap: 5px;
            white-space: nowrap;
        }
        .pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-emerald); box-shadow: 0 0 8px var(--accent-emerald); }

        /* Centered Place Pill (like screenshot) */
        .place-pill {
            background: #131c31; border: 1px solid var(--border);
            border-radius: 999px; padding: 6px 20px; font-size: 0.85rem; font-weight: 700;
            color: #fff; box-shadow: 0 4px 14px rgba(0,0,0,0.35);
            display: flex; align-items: center; gap: 8px; cursor: pointer;
        }
        .place-pill small { font-weight: 500; color: var(--accent-cyan); font-size: 0.75rem; }

        /* Top Right Search + Actions */
        .top-right { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
        .top-search-wrap { position: relative; width: 255px; }
        .top-search {
            width: 100%; background: var(--bg-input); border: 1px solid var(--border);
            border-radius: 999px; padding: 7px 30px 7px 14px; color: #fff; font-size: 0.8rem; outline: none;
        }
        .top-search:focus { border-color: var(--accent-cyan); }
        .search-clear {
            position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
            background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.95rem; display: none;
        }
        .autocomplete-box {
            position: absolute; top: calc(100% + 6px); left: 0; right: 0; min-width: 310px;
            background: #0f172a; border: 1px solid var(--border-active); border-radius: 10px;
            max-height: 290px; overflow-y: auto; z-index: 1400; display: none;
            box-shadow: 0 14px 30px rgba(0,0,0,0.75);
        }
        .ac-item { padding: 9px 12px; border-bottom: 1px solid var(--border); cursor: pointer; }
        .ac-item:hover { background: rgba(56, 189, 248, 0.12); }
        .ac-title { font-size: 0.8rem; font-weight: 600; color: #fff; display: block; }
        .ac-sub { font-size: 0.7rem; color: var(--text-muted); display: block; margin-top: 2px; }

        .top-btn {
            padding: 6px 11px; border-radius: 8px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.04); color: var(--text-muted);
            font-size: 0.76rem; font-weight: 600; cursor: pointer; text-decoration: none; white-space: nowrap;
        }
        .top-btn:hover, .top-btn.active { color: #fff; border-color: var(--accent-cyan); background: rgba(56, 189, 248, 0.14); }

        /* Stage */
        .stage { position: relative; flex: 1; overflow: hidden; }
        #mapView { position: absolute; inset: 0; }
        #map { width: 100%; height: 100%; background: #070b14; }

        /* Left Vertical Tool Rail (Regrid-inspired, dark modern UI) */
        .tool-rail {
            position: absolute; top: 14px; left: 14px; width: 112px;
            background: var(--bg-panel); backdrop-filter: blur(18px);
            border: 1px solid var(--border); border-radius: 14px;
            z-index: 1050; padding: 8px 6px; display: flex; flex-direction: column; gap: 3px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.6);
            transition: transform 0.22s ease;
        }
        .tool-rail.hidden { transform: translateX(-140px); }

        .rail-btn {
            display: flex; align-items: center; gap: 8px; width: 100%;
            padding: 8px 10px; border-radius: 9px; border: none; background: transparent;
            color: var(--text-muted); font-size: 0.78rem; font-weight: 600; cursor: pointer;
            transition: all 0.15s; text-align: left;
        }
        .rail-btn:hover { background: rgba(255,255,255,0.06); color: #fff; }
        .rail-btn.active { background: rgba(20, 184, 166, 0.2); color: #5eead4; }
        .rail-badge {
            margin-left: auto; font-size: 0.65rem; padding: 1px 5px; border-radius: 999px;
            background: rgba(56, 189, 248, 0.2); color: var(--accent-cyan);
        }

        /* Bottom-Left Tools Toggle Pill */
        .tools-toggle-btn {
            position: absolute; bottom: 16px; left: 14px; z-index: 1060;
            background: #0f766e; color: #fff; border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px; padding: 8px 14px; font-size: 0.8rem; font-weight: 700;
            cursor: pointer; display: flex; align-items: center; gap: 6px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        .tools-toggle-btn:hover { background: #0d9488; }

        /* Expandable Tool Drawer (opens right next to the tool rail!) */
        .tool-panel {
            position: absolute; top: 14px; left: 136px; bottom: 64px; width: 325px;
            background: var(--bg-panel); backdrop-filter: blur(20px);
            border: 1px solid var(--border); border-radius: 14px;
            z-index: 1045; display: none; flex-direction: column;
            box-shadow: 0 20px 50px rgba(0,0,0,0.65); overflow: hidden;
        }
        .tool-panel.open { display: flex; }
        .tool-rail.hidden ~ .tool-panel.open { left: 14px; }

        .panel-header {
            padding: 13px 16px; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .panel-header h3 { font-size: 0.9rem; font-weight: 700; }
        .close-x {
            background: rgba(255,255,255,0.06); border: 1px solid var(--border);
            color: var(--text-muted); width: 26px; height: 26px; border-radius: 6px;
            cursor: pointer; font-size: 1rem; display: grid; place-items: center;
        }
        .close-x:hover { color: #fff; }
        .panel-body { flex: 1; overflow-y: auto; padding: 14px 16px; display: flex; flex-direction: column; gap: 12px; }

        /* Filter Form Controls */
        .f-group { display: flex; flex-direction: column; gap: 5px; }
        .f-label { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
        .f-input, .f-select {
            width: 100%; background: var(--bg-input); border: 1px solid var(--border);
            border-radius: 8px; padding: 8px 10px; color: #fff; font-size: 0.8rem; outline: none;
        }
        .f-input:focus, .f-select:focus { border-color: var(--accent-cyan); }
        .f-row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .btn-primary {
            padding: 9px 12px; border-radius: 8px; border: none;
            background: linear-gradient(135deg, #0d9488, #0284c7); color: #fff;
            font-size: 0.8rem; font-weight: 700; cursor: pointer;
        }
        .btn-ghost {
            padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.04); color: var(--text-muted);
            font-size: 0.78rem; font-weight: 600; cursor: pointer;
        }
        .btn-ghost:hover { color: #fff; border-color: var(--accent-cyan); }

        /* Property Detail Card (opens when parcel is clicked!) */
        .parcel-card {
            position: absolute; top: 14px; left: 136px; bottom: 64px; width: 345px;
            background: var(--bg-panel); backdrop-filter: blur(22px);
            border: 1px solid var(--border-active); border-radius: 14px;
            z-index: 1080; display: none; flex-direction: column;
            box-shadow: 0 24px 60px rgba(0,0,0,0.75); overflow: hidden;
        }
        .parcel-card.open { display: flex; }
        .parcel-card.shifted { left: 470px; }

        .pc-head {
            padding: 14px 16px; border-bottom: 1px solid var(--border);
            background: linear-gradient(135deg, rgba(13, 148, 136, 0.14), rgba(2, 132, 199, 0.1));
            position: relative;
        }
        .pc-title { font-size: 0.98rem; font-weight: 800; margin-right: 32px; line-height: 1.3; }
        .pc-sub { font-size: 0.76rem; color: var(--text-muted); margin-top: 3px; }
        .pc-actions-row { display: flex; gap: 8px; margin-top: 10px; align-items: center; }
        .follow-btn {
            padding: 5px 11px; border-radius: 999px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.06); color: #fff; font-size: 0.73rem; font-weight: 700; cursor: pointer;
        }
        .follow-btn.following { background: rgba(251, 191, 36, 0.2); border-color: var(--accent-amber); color: var(--accent-amber); }

        .pc-tabs { display: flex; border-bottom: 1px solid var(--border); background: rgba(7,11,20,0.5); }
        .pc-tab {
            flex: 1; padding: 9px 6px; border: none; background: transparent;
            color: var(--text-muted); font-size: 0.75rem; font-weight: 600; cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        .pc-tab.active { color: #fff; border-bottom-color: var(--accent-teal); }

        .pc-body { flex: 1; overflow-y: auto; padding: 14px 16px; }
        .kv-table { width: 100%; border-collapse: collapse; font-size: 0.79rem; }
        .kv-table td { padding: 7px 2px; border-bottom: 1px solid var(--border); vertical-align: top; }
        .kv-table td:first-child { color: var(--text-muted); width: 44%; }
        .kv-table td:last-child { color: #fff; font-weight: 600; text-align: right; word-break: break-word; }

        .stat-grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 7px; margin-bottom: 12px; }
        .sg-box { background: var(--bg-input); border: 1px solid var(--border); border-radius: 9px; padding: 8px; text-align: center; }
        .sg-v { font-size: 0.88rem; font-weight: 800; color: #fff; }
        .sg-l { font-size: 0.64rem; color: var(--text-muted); text-transform: uppercase; margin-top: 2px; }

        /* Right Layers Panel (toggled by bottom-right Layers button!) */
        .layers-panel {
            position: absolute; top: 14px; right: 14px; bottom: 94px; width: 320px;
            background: var(--bg-panel); backdrop-filter: blur(20px);
            border: 1px solid var(--border); border-radius: 14px;
            z-index: 1090; display: none; flex-direction: column;
            box-shadow: 0 24px 60px rgba(0,0,0,0.75); overflow: hidden;
        }
        .layers-panel.open { display: flex; }

        .layer-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .l-card {
            border: 1px solid var(--border); border-radius: 10px; padding: 10px;
            background: rgba(255,255,255,0.03); cursor: pointer; transition: all 0.15s;
            display: flex; flex-direction: column; gap: 4px;
        }
        .l-card:hover { border-color: rgba(255,255,255,0.35); }
        .l-card.active { border-color: var(--accent-teal); background: rgba(20, 184, 166, 0.16); }
        .l-card-title { font-size: 0.78rem; font-weight: 700; color: #fff; }
        .l-card-sub { font-size: 0.67rem; color: var(--text-muted); }

        .layers-toggle-btn {
            position: absolute; bottom: 16px; right: 56px; z-index: 1060;
            background: var(--bg-panel); backdrop-filter: blur(14px);
            color: #fff; border: 1px solid var(--border); border-radius: 10px;
            padding: 8px 14px; font-size: 0.79rem; font-weight: 700; cursor: pointer;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        .layers-toggle-btn.active { border-color: var(--accent-teal); background: rgba(15, 118, 110, 0.9); }

        .usa-reset-btn {
            position: absolute; bottom: 16px; right: 150px; z-index: 1060;
            background: var(--bg-panel); backdrop-filter: blur(14px);
            color: #fff; border: 1px solid var(--border); border-radius: 10px;
            padding: 8px 12px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
        }
        .usa-reset-btn:hover { border-color: var(--accent-cyan); }

        /* Measure Banner */
        .measure-banner {
            position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
            z-index: 1150; background: rgba(15, 23, 42, 0.95); border: 1px solid var(--accent-pink);
            color: #fff; padding: 8px 16px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
            display: none; align-items: center; gap: 10px; box-shadow: 0 10px 30px rgba(255,42,122,0.3);
        }

        /* List Items inside Panel */
        .list-card {
            background: rgba(255,255,255,0.03); border: 1px solid var(--border);
            border-radius: 10px; padding: 10px; cursor: pointer; transition: border-color 0.15s;
        }
        .list-card:hover { border-color: var(--accent-cyan); background: rgba(56, 189, 248, 0.08); }
        .cat-pill {
            font-size: 0.65rem; font-weight: 700; padding: 2px 7px; border-radius: 4px;
            background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); text-transform: uppercase;
        }

        /* Parcel Text Labels (Owner / APN / Acres) */
        .parcel-map-label {
            background: rgba(7, 11, 20, 0.82); color: #f8fafc;
            border: 1px solid rgba(255,255,255,0.2); border-radius: 4px;
            padding: 1px 5px; font-size: 10px; font-weight: 600; white-space: nowrap;
            pointer-events: none; box-shadow: 0 2px 6px rgba(0,0,0,0.5);
        }

        /* Overlay Legend Pill */
        .overlay-legend {
            position: absolute; bottom: 16px; left: 136px; z-index: 1000;
            background: var(--bg-panel); backdrop-filter: blur(12px);
            border: 1px solid var(--border); border-radius: 999px;
            padding: 6px 14px; display: flex; flex-wrap: wrap; gap: 12px;
            font-size: 0.72rem; color: var(--text-muted);
        }
        .leg-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }

        /* Full Table / Analytics View */
        #tableView {
            position: absolute; inset: 0; overflow-y: auto; padding: 24px 28px;
            background: var(--bg-dark); display: none;
        }
        .tv-container { max-width: 1420px; margin: 0 auto; }
        .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-bottom: 20px; }
        .kpi-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
        .kpi-lbl { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .kpi-num { font-size: 1.6rem; font-weight: 800; margin-top: 4px; }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(305px, 1fr)); gap: 14px; }
        .grid-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 15px; display: flex; flex-direction: column; gap: 7px; }
        .grid-card:hover { border-color: var(--accent-cyan); }

        .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {
            background-color: rgba(20, 184, 166, 0.28) !important;
        }
        .marker-cluster-small div, .marker-cluster-medium div, .marker-cluster-large div {
            background-color: rgba(13, 148, 136, 0.92) !important;
            color: #fff !important; font-weight: 700 !important;
        }

        @media (max-width: 900px) {
            .topbar { grid-template-columns: 1fr auto; }
            .place-pill, .status-pill { display: none; }
            .top-search-wrap { width: 170px; }
            .tool-panel, .parcel-card, .layers-panel { width: calc(100% - 28px); left: 14px !important; }
            .overlay-legend { display: none; }
        }
    </style>
</head>
<body>

    <header class="topbar">
        <div class="brand-wrap">
            <div class="brand">
                <div class="brand-icon">🗺️</div>
                <span>ParcelScope US</span>
            </div>
            <span class="status-pill" id="apiStatusPill"><span class="pulse-dot"></span> __TOTAL_COUNT__ Parcels • 50 States</span>
        </div>

        <div class="place-pill" onclick="resetUSAView()" title="Click to reset to Nationwide USA view">
            <span id="placeLabel">United States (Nationwide)</span>
            <small id="placeCount">__TOTAL_COUNT__ marked</small>
        </div>

        <div class="top-right">
            <div class="top-search-wrap">
                <input type="text" id="topSearchInput" class="top-search" placeholder="Search address, city, APN, owner..." oninput="onTopSearch()" autocomplete="off">
                <button class="search-clear" id="searchClearBtn" onclick="clearSearch()">&times;</button>
                <div class="autocomplete-box" id="autocompleteBox"></div>
            </div>
            <button class="top-btn active" id="btnMapMode" onclick="switchMode('map')">🗺️ Map</button>
            <button class="top-btn" id="btnTableMode" onclick="switchMode('table')">📊 Grid</button>
            <a href="/docs" target="_blank" class="top-btn">API Docs ↗</a>
        </div>
    </header>

    <div class="stage">
        <!-- MAP VIEW -->
        <div id="mapView">
            <div id="map"></div>

            <!-- Measurement Banner -->
            <div class="measure-banner" id="measureBanner">
                <span id="measureText">📏 Click points on the map to measure distance & area</span>
                <button class="btn-ghost" style="padding:3px 9px;" onclick="clearMeasure()">Clear</button>
                <button class="btn-ghost" style="padding:3px 9px;" onclick="toggleMeasure()">Done</button>
            </div>

            <!-- Left Vertical Tools Rail -->
            <nav class="tool-rail" id="toolRail">
                <button class="rail-btn" data-tool="insights" onclick="openTool('insights', this)">📊 Insights</button>
                <button class="rail-btn" data-tool="following" onclick="openTool('following', this)">⭐ Saved <span class="rail-badge" id="savedBadge">0</span></button>
                <button class="rail-btn active" data-tool="filter" onclick="openTool('filter', this)">▽ Filter <span class="rail-badge" id="filterCountBadge">__TOTAL_COUNT__</span></button>
                <button class="rail-btn" data-tool="export" onclick="openTool('export', this)">⬇ Export</button>
                <button class="rail-btn" data-tool="measure" id="railMeasureBtn" onclick="toggleMeasure()">📏 Measure</button>
                <button class="rail-btn" data-tool="style" onclick="openTool('style', this)">🎨 Style</button>
                <button class="rail-btn" data-tool="list" onclick="openTool('list', this)">☰ List</button>
                <button class="rail-btn" onclick="window.print()">🖨 Print</button>
            </nav>

            <!-- Bottom-Left Tools Toggle -->
            <button class="tools-toggle-btn" onclick="toggleToolRail()">🛠️ Tools</button>

            <!-- Expandable Tool Drawer -->
            <aside class="tool-panel open" id="toolPanel">
                <div class="panel-header">
                    <h3 id="toolPanelTitle">Property & Parcel Filters</h3>
                    <button class="close-x" onclick="closeToolPanel()">&times;</button>
                </div>
                <div class="panel-body" id="toolPanelBody">
                    <!-- Populated dynamically per selected tool -->
                </div>
            </aside>

            <!-- Floating Selected Parcel / Property Card -->
            <aside class="parcel-card" id="parcelCard">
                <div class="pc-head">
                    <button class="close-x" style="position:absolute; top:12px; right:12px;" onclick="closeParcelCard()">&times;</button>
                    <div class="pc-title" id="pcTitle">6801 Emmett F Lowry Expy</div>
                    <div class="pc-sub" id="pcSub">Texas City, TX 77591</div>
                    <div class="pc-actions-row">
                        <button class="follow-btn" id="pcFollowBtn" onclick="toggleFollowCurrent()">☆ SAVE PARCEL</button>
                        <button class="follow-btn" onclick="zoomToCurrent()">🎯 ZOOM IN</button>
                    </div>
                </div>
                <div class="pc-tabs">
                    <button class="pc-tab active" onclick="setCardTab('parcel', this)">Parcel Data</button>
                    <button class="pc-tab" onclick="setCardTab('owner', this)">Owner Info</button>
                    <button class="pc-tab" onclick="setCardTab('gis', this)">GIS & API</button>
                </div>
                <div class="pc-body" id="pcBody"></div>
            </aside>

            <!-- Right Layers Drawer (Basemaps + Labels + Additional GIS Overlays) -->
            <aside class="layers-panel" id="layersPanel">
                <div class="panel-header">
                    <h3>Layers</h3>
                    <button class="close-x" onclick="toggleLayersPanel()">&times;</button>
                </div>
                <div class="panel-body">
                    <div class="f-label">Base Maps</div>
                    <div class="layer-cards">
                        <div class="l-card active" onclick="setBaseMap('satellite1', this)">
                            <span class="l-card-title">🛰️ Satellite 1</span>
                            <span class="l-card-sub">Aerial + Road Labels</span>
                        </div>
                        <div class="l-card" onclick="setBaseMap('satellite2', this)">
                            <span class="l-card-title">🛰️ Satellite 2</span>
                            <span class="l-card-sub">Clean Aerial Imagery</span>
                        </div>
                        <div class="l-card" onclick="setBaseMap('street', this)">
                            <span class="l-card-title">🗺️ Street</span>
                            <span class="l-card-sub">Vector Road & Lot Grid</span>
                        </div>
                        <div class="l-card" onclick="setBaseMap('dark', this)">
                            <span class="l-card-title">🌑 Dark Canvas</span>
                            <span class="l-card-sub">Esri Dark Gray</span>
                        </div>
                    </div>

                    <div class="f-label" style="margin-top:6px;">Parcel Map Labels (Zoom 14+)</div>
                    <div class="layer-cards">
                        <div class="l-card" id="lblOwnerCard" onclick="toggleMapLabel('owner', this)">
                            <span class="l-card-title">👤 Owner Names</span>
                            <span class="l-card-sub">Show on parcel lots</span>
                        </div>
                        <div class="l-card" id="lblApnCard" onclick="toggleMapLabel('apn', this)">
                            <span class="l-card-title">🔢 Parcel Numbers</span>
                            <span class="l-card-sub">APN on every lot</span>
                        </div>
                        <div class="l-card" id="lblAcresCard" onclick="toggleMapLabel('acres', this)">
                            <span class="l-card-title">📐 Lot Acreage</span>
                            <span class="l-card-sub">Acres per boundary</span>
                        </div>
                    </div>

                    <div class="f-label" style="margin-top:6px;">Additional Spatial Overlays</div>
                    <div class="layer-cards">
                        <div class="l-card active" id="ovOutlinesCard" onclick="toggleOverlay('outlines', this)">
                            <span class="l-card-title">🟨 Parcel Outlines</span>
                            <span class="l-card-sub">All 3,963 marked lots</span>
                        </div>
                        <div class="l-card" id="ovZoningCard" onclick="toggleOverlay('zoning', this)">
                            <span class="l-card-title">🎨 Standardized Zoning</span>
                            <span class="l-card-sub">Color by R-1 / C-2 / M-1</span>
                        </div>
                        <div class="l-card" id="ovValueCard" onclick="toggleOverlay('value', this)">
                            <span class="l-card-title">💰 Valuation Shading</span>
                            <span class="l-card-sub">Shade by assessed tier</span>
                        </div>
                    </div>
                </div>
            </aside>

            <!-- Bottom Map Action Buttons & Legend -->
            <div class="overlay-legend" id="overlayLegend">
                <span><span class="leg-dot" style="background:#38bdf8;"></span>Residential</span>
                <span><span class="leg-dot" style="background:#fbbf24;"></span>Commercial</span>
                <span><span class="leg-dot" style="background:#34d399;"></span>Land & Vacant</span>
                <span><span class="leg-dot" style="background:#a78bfa;"></span>Industrial</span>
                <span><span class="leg-dot" style="background:#ff2a7a;"></span>Selected Parcel</span>
            </div>

            <button class="usa-reset-btn" onclick="zoomToSampleLot()">🔍 Inspect Lot</button>
            <button class="layers-toggle-btn" id="layersBtn" onclick="toggleLayersPanel()">🗂️ Layers</button>
        </div>

        <!-- TABLE / GRID ANALYTICS VIEW -->
        <div id="tableView">
            <div class="tv-container">
                <div class="kpi-row">
                    <div class="kpi-box"><div class="kpi-lbl">Total Mapped Parcels</div><div class="kpi-num" style="color:var(--accent-cyan);">__TOTAL_COUNT__</div></div>
                    <div class="kpi-box"><div class="kpi-lbl">Filtered Matches</div><div class="kpi-num" id="tvMatchNum" style="color:var(--accent-emerald);">__TOTAL_COUNT__</div></div>
                    <div class="kpi-box"><div class="kpi-lbl">Total Acreage (Filtered)</div><div class="kpi-num" id="tvAcresNum" style="color:var(--accent-amber);">0</div></div>
                    <div class="kpi-box"><div class="kpi-lbl">US Coverage</div><div class="kpi-num" style="color:#fff;">50 States</div></div>
                </div>
                <div class="cards-grid" id="tvGrid"></div>
                <div style="display:flex; justify-content:center; gap:12px; margin:24px 0;">
                    <button class="btn-ghost" id="tvPrev" onclick="changeGridPage(-1)">← Previous</button>
                    <span id="tvPageLbl" style="padding:8px; font-size:0.84rem; color:var(--text-muted);">Page 1</span>
                    <button class="btn-ghost" id="tvNext" onclick="changeGridPage(1)">Next →</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ALL_PROPERTIES = __COMPACT_JSON__;
        let filtered = ALL_PROPERTIES;
        let selectedProp = null;
        let activeCardTab = 'parcel';
        let activeTool = 'filter';
        let currentPage = 1;
        const PAGE_SIZE = 48;

        // Saved / Followed Parcels in localStorage
        let savedIds = new Set(JSON.parse(localStorage.getItem('parcelscope_saved') || '[]'));

        // Filter State (100% Unified Real Estate Filters - No Source URL filters!)
        const filters = {
            search: '',
            category: 'all',
            status: 'all',
            state: 'all',
            city: '',
            zoning: 'all',
            owner: '',
            minPrice: '',
            maxPrice: '',
            minAcres: '',
            maxAcres: ''
        };

        // Visual Style & Overlay State
        const mapState = {
            base: 'satellite1',
            showOutlines: true,
            overlayMode: 'default', // 'default' | 'zoning' | 'value'
            labelMode: null,        // null | 'owner' | 'apn' | 'acres'
            outlineColor: 'auto',   // 'auto' | '#facc15' | '#0f766e' | '#38bdf8' | '#ffffff'
            highlightColor: '#ff2a7a',
            lineWeight: 1.8,
            fillOpacity: 0.16
        };

        // --- MAP SETUP ---
        const map = L.map('map', {
            center: [38.5, -96.5],
            zoom: 4,
            zoomControl: false,
            preferCanvas: true
        });
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        const baseLayers = {
            satellite1: L.layerGroup([
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19, attribution: 'Powered by Esri' }),
                L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })
            ]),
            satellite2: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19, attribution: 'Powered by Esri' }),
            street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap' }),
            dark: L.layerGroup([
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', { maxNativeZoom: 16, maxZoom: 19, attribution: 'Powered by Esri' }),
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', { maxNativeZoom: 16, maxZoom: 19 })
            ])
        };
        baseLayers.satellite1.addTo(map);

        const clusterLayer = L.markerClusterGroup({
            chunkedLoading: true,
            maxClusterRadius: 45,
            disableClusteringAtZoom: 13
        });
        map.addLayer(clusterLayer);

        const polygonLayer = L.layerGroup().addTo(map);
        const labelLayer = L.layerGroup().addTo(map);
        const highlightLayer = L.layerGroup().addTo(map);
        const measureLayer = L.layerGroup().addTo(map);

        function fmtMoney(v) {
            if (v === null || v === undefined) return 'N/A';
            return '$' + Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 });
        }

        function getCategoryColor(cat) {
            if (cat === 'Commercial') return '#fbbf24';
            if (cat === 'Land & Vacant') return '#34d399';
            if (cat === 'Industrial') return '#a78bfa';
            if (cat === 'Multi-Family') return '#f472b6';
            return '#38bdf8';
        }

        function getParcelStyle(p) {
            let stroke = mapState.outlineColor;
            if (stroke === 'auto') {
                stroke = (mapState.base === 'street') ? '#0f766e' : '#facc15';
            }
            let fill = stroke;
            let op = mapState.fillOpacity;

            if (mapState.overlayMode === 'zoning') {
                fill = getCategoryColor(p.category);
                stroke = fill;
                op = Math.max(0.32, mapState.fillOpacity);
            } else if (mapState.overlayMode === 'value') {
                const v = p.price || p.tax_assessed_value || 0;
                fill = v >= 2000000 ? '#f43f5e' : (v >= 500000 ? '#fbbf24' : '#34d399');
                stroke = fill;
                op = Math.max(0.35, mapState.fillOpacity);
            }
            return { color: stroke, weight: mapState.lineWeight, fillColor: fill, fillOpacity: op };
        }

        // --- MAP RENDERING ---
        function renderClusters(items) {
            clusterLayer.clearLayers();
            const markers = [];
            for (let i = 0; i < items.length; i++) {
                const p = items[i];
                if (p.latitude == null || p.longitude == null) continue;
                const c = getCategoryColor(p.category);
                const m = L.circleMarker([p.latitude, p.longitude], {
                    radius: 6, color: '#070b14', weight: 1.5, fillColor: c, fillOpacity: 0.9
                });
                m.on('click', () => { if (!measureActive) selectParcel(p, false); });
                markers.push(m);
            }
            clusterLayer.addLayers(markers);
        }

        function renderPolygonsAndLabels() {
            polygonLayer.clearLayers();
            labelLayer.clearLayers();
            const z = map.getZoom();
            if (!mapState.showOutlines || z < 11) return;

            const bounds = map.getBounds();
            let count = 0;
            for (let i = 0; i < filtered.length; i++) {
                const p = filtered[i];
                if (p.latitude == null || p.longitude == null) continue;
                if (!bounds.contains([p.latitude, p.longitude])) continue;

                const geom = p.raw_data && p.raw_data.geojson_geometry;
                if (geom) {
                    const poly = L.geoJSON(geom, { style: getParcelStyle(p) });
                    poly.on('click', () => { if (!measureActive) selectParcel(p, false); });
                    polygonLayer.addLayer(poly);
                }

                if (mapState.labelMode && z >= 14 && count < 120) {
                    let lblText = '';
                    if (mapState.labelMode === 'owner') lblText = (p.owner_name || 'Owner').slice(0, 22);
                    else if (mapState.labelMode === 'apn') lblText = p.parcel_id || p.external_id || '';
                    else if (mapState.labelMode === 'acres') lblText = (p.lot_size_acres ? p.lot_size_acres + ' AC' : '');
                    if (lblText) {
                        const lbl = L.marker([p.latitude, p.longitude], {
                            interactive: false,
                            icon: L.divIcon({ className: 'parcel-map-label', html: lblText, iconSize: null })
                        });
                        labelLayer.addLayer(lbl);
                    }
                }
                count++;
                if (count >= 450) break;
            }
        }
        map.on('moveend zoomend', renderPolygonsAndLabels);

        // --- SELECT & INSPECT PARCEL ---
        function selectParcel(p, fly = true) {
            selectedProp = p;
            highlightLayer.clearLayers();

            if (p.latitude != null && p.longitude != null) {
                if (fly) map.flyTo([p.latitude, p.longitude], 16, { duration: 0.85 });
                const geom = p.raw_data && p.raw_data.geojson_geometry;
                if (geom) {
                    L.geoJSON(geom, {
                        style: { color: mapState.highlightColor, weight: 4, fillColor: mapState.highlightColor, fillOpacity: 0.3 }
                    }).addTo(highlightLayer);
                } else {
                    L.circleMarker([p.latitude, p.longitude], {
                        radius: 12, color: mapState.highlightColor, weight: 3.5, fillColor: mapState.highlightColor, fillOpacity: 0.35
                    }).addTo(highlightLayer);
                }
            }

            document.getElementById('placeLabel').innerText = `${p.city || 'US'}, ${p.state || ''}`;
            renderParcelCard();
        }

        function renderParcelCard() {
            const p = selectedProp;
            if (!p) return;
            const card = document.getElementById('parcelCard');
            card.classList.add('open');
            card.classList.toggle('shifted', document.getElementById('toolPanel').classList.contains('open'));

            document.getElementById('pcTitle').innerText = p.address || p.title || p.external_id;
            document.getElementById('pcSub').innerText = `${p.city || ''}${p.county ? ' • ' + p.county : ''}, ${p.state || ''} ${p.zip_code || ''}`;

            const fBtn = document.getElementById('pcFollowBtn');
            const isSaved = savedIds.has(p.id);
            fBtn.innerText = isSaved ? '★ SAVED' : '☆ SAVE PARCEL';
            fBtn.classList.toggle('following', isSaved);

            const rd = p.raw_data || {};
            const body = document.getElementById('pcBody');
            const primaryVal = p.price ? fmtMoney(p.price) : (p.lease_rate || fmtMoney(p.tax_assessed_value));

            if (activeCardTab === 'parcel') {
                body.innerHTML = `
                    <div class="stat-grid3">
                        <div class="sg-box"><div class="sg-v" style="color:var(--accent-emerald);">${primaryVal}</div><div class="sg-l">${p.price ? 'List Price' : (p.lease_rate ? 'Lease Rate' : 'Assessed')}</div></div>
                        <div class="sg-box"><div class="sg-v">${p.lot_size_acres ? p.lot_size_acres + ' AC' : '-'}</div><div class="sg-l">Lot Acreage</div></div>
                        <div class="sg-box"><div class="sg-v">${p.sqft ? p.sqft.toLocaleString() : '-'}</div><div class="sg-l">Bldg SqFt</div></div>
                    </div>
                    <table class="kv-table">
                        <tr><td>Parcel ID / APN</td><td>${p.parcel_id || p.external_id}</td></tr>
                        <tr><td>Property Category</td><td>${p.category} (${p.property_type || '-'})</td></tr>
                        <tr><td>Market Status</td><td>${(p.listing_status || 'active').replace('_', ' ').toUpperCase()}</td></tr>
                        <tr><td>Zoning Code</td><td>${p.zoning || '-'}</td></tr>
                        <tr><td>County Assessed Value</td><td>${fmtMoney(p.tax_assessed_value)}</td></tr>
                        <tr><td>Land / Improvement</td><td>${fmtMoney(rd.land_value)} / ${fmtMoney(rd.improvement_value)}</td></tr>
                        <tr><td>Annual Tax (${rd.tax_year || 2025})</td><td>${fmtMoney(rd.tax_amount)}</td></tr>
                        <tr><td>Last Deed Sale</td><td>${fmtMoney(rd.last_sale_price)} (${rd.last_sale_date || '-'})</td></tr>
                        <tr><td>Beds / Baths / Year</td><td>${p.beds || '-'} / ${p.baths || '-'} / ${p.year_built || '-'}</td></tr>
                        <tr><td>Legal Description</td><td>${p.legal_description || '-'}</td></tr>
                    </table>
                `;
            } else if (activeCardTab === 'owner') {
                body.innerHTML = `
                    <table class="kv-table">
                        <tr><td>Registered Deed Owner</td><td>${p.owner_name || 'N/A'}</td></tr>
                        <tr><td>Owner Mailing Address</td><td>${rd.owner_mailing || (p.city ? p.city + ', ' + p.state : '-')}</td></tr>
                        <tr><td>County Jurisdiction</td><td>${p.county || '-'}, ${p.state || '-'}</td></tr>
                        <tr><td>County FIPS Code</td><td>${rd.fips || '-'}</td></tr>
                        <tr><td>Broker / Agent</td><td>${p.broker_name || 'County Tax Assessor'}</td></tr>
                        <tr><td>Tax Exemptions</td><td>${rd.exemptions || 'Standard Assessment'}</td></tr>
                    </table>
                `;
            } else {
                const geomStr = rd.geojson_geometry ? JSON.stringify(rd.geojson_geometry, null, 2) : 'Point Geometry';
                body.innerHTML = `
                    <table class="kv-table" style="margin-bottom:12px;">
                        <tr><td>Universal Record ID</td><td style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;">${rd.ll_uuid || p.id}</td></tr>
                        <tr><td>Latitude / Longitude</td><td>${p.latitude}, ${p.longitude}</td></tr>
                        <tr><td>Live Database Endpoint</td><td><a href="/api/v1/properties/${p.id}" target="_blank" style="color:var(--accent-cyan);">/api/v1/properties/${p.id} ↗</a></td></tr>
                    </table>
                    <div style="font-size:0.72rem; color:var(--text-muted); font-weight:600; margin-bottom:6px; display:flex; justify-content:space-between;">
                        <span>PARCEL BOUNDARY (GEOJSON)</span>
                        <button type="button" onclick="copyGeom()" style="background:none; border:none; color:var(--accent-cyan); font-size:0.72rem; font-weight:600; cursor:pointer;">Copy JSON</button>
                    </div>
                    <pre style="background:var(--bg-input); border:1px solid var(--border); border-radius:8px; padding:10px; font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--accent-teal); max-height:160px; overflow:auto;">${geomStr}</pre>
                `;
            }
        }

        function setCardTab(tab, el) {
            activeCardTab = tab;
            document.querySelectorAll('.pc-tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            renderParcelCard();
        }

        function closeParcelCard() {
            document.getElementById('parcelCard').classList.remove('open');
            highlightLayer.clearLayers();
        }

        function zoomToCurrent() {
            if (selectedProp && selectedProp.latitude) map.flyTo([selectedProp.latitude, selectedProp.longitude], 17, { duration: 0.7 });
        }

        function toggleFollowCurrent() {
            if (!selectedProp) return;
            if (savedIds.has(selectedProp.id)) savedIds.delete(selectedProp.id);
            else savedIds.add(selectedProp.id);
            localStorage.setItem('parcelscope_saved', JSON.stringify([...savedIds]));
            document.getElementById('savedBadge').innerText = savedIds.size;
            renderParcelCard();
            if (activeTool === 'following') renderToolContent();
        }

        function copyGeom() {
            if (!selectedProp || !selectedProp.raw_data || !selectedProp.raw_data.geojson_geometry) return;
            navigator.clipboard.writeText(JSON.stringify(selectedProp.raw_data.geojson_geometry, null, 2));
        }

        // --- LEFT TOOL RAIL & PANEL CONTENT ---
        function toggleToolRail() {
            document.getElementById('toolRail').classList.toggle('hidden');
        }

        function closeToolPanel() {
            document.getElementById('toolPanel').classList.remove('open');
            document.getElementById('parcelCard').classList.remove('shifted');
            document.querySelectorAll('.rail-btn').forEach(b => b.classList.remove('active'));
        }

        function openTool(name, btn) {
            const panel = document.getElementById('toolPanel');
            if (activeTool === name && panel.classList.contains('open')) {
                closeToolPanel();
                return;
            }
            activeTool = name;
            document.querySelectorAll('.rail-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            panel.classList.add('open');
            if (document.getElementById('parcelCard').classList.contains('open')) {
                document.getElementById('parcelCard').classList.add('shifted');
            }
            renderToolContent();
        }

        function renderToolContent() {
            const title = document.getElementById('toolPanelTitle');
            const body = document.getElementById('toolPanelBody');

            if (activeTool === 'filter') {
                title.innerText = `Filters (${filtered.length.toLocaleString()} matches)`;
                body.innerHTML = `
                    <div class="f-group">
                        <label class="f-label">Property Category</label>
                        <select class="f-select" onchange="updateFilter('category', this.value, false)">
                            <option value="all" ${filters.category==='all'?'selected':''}>All Property Types</option>
                            <option value="Residential" ${filters.category==='Residential'?'selected':''}>🏡 Residential</option>
                            <option value="Commercial" ${filters.category==='Commercial'?'selected':''}>🏢 Commercial</option>
                            <option value="Land & Vacant" ${filters.category==='Land & Vacant'?'selected':''}>🌾 Land & Vacant Parcels</option>
                            <option value="Industrial" ${filters.category==='Industrial'?'selected':''}>🏭 Industrial & Warehouse</option>
                            <option value="Multi-Family" ${filters.category==='Multi-Family'?'selected':''}>🏘️ Multi-Family</option>
                        </select>
                    </div>
                    <div class="f-row2">
                        <div class="f-group">
                            <label class="f-label">US State</label>
                            <select class="f-select" id="stateSelectFilter" onchange="updateFilter('state', this.value, true)">
                                <option value="all">All 50 States</option>
                                ${["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"].map(s => `<option value="${s}" ${filters.state===s?'selected':''}>${s}</option>`).join('')}
                            </select>
                        </div>
                        <div class="f-group">
                            <label class="f-label">Market Status</label>
                            <select class="f-select" onchange="updateFilter('status', this.value, false)">
                                <option value="all" ${filters.status==='all'?'selected':''}>All Statuses</option>
                                <option value="for_sale" ${filters.status==='for_sale'?'selected':''}>For Sale</option>
                                <option value="for_lease" ${filters.status==='for_lease'?'selected':''}>For Lease</option>
                                <option value="off_market" ${filters.status==='off_market'?'selected':''}>Off-Market / Parcel</option>
                            </select>
                        </div>
                    </div>
                    <div class="f-group">
                        <label class="f-label">City or County</label>
                        <input class="f-input" type="text" placeholder="e.g. Austin, Harris County..." value="${filters.city}" oninput="updateFilter('city', this.value, false)">
                    </div>
                    <div class="f-group">
                        <label class="f-label">Zoning Classification</label>
                        <select class="f-select" onchange="updateFilter('zoning', this.value, false)">
                            <option value="all" ${filters.zoning==='all'?'selected':''}>All Zoning Codes</option>
                            <option value="R-1" ${filters.zoning==='R-1'?'selected':''}>R-1 Residential</option>
                            <option value="C-2" ${filters.zoning==='C-2'?'selected':''}>C-2 Commercial</option>
                            <option value="C-3" ${filters.zoning==='C-3'?'selected':''}>C-3 Heavy Commercial</option>
                            <option value="M-1" ${filters.zoning==='M-1'?'selected':''}>M-1 Industrial</option>
                            <option value="Agricultural" ${filters.zoning==='Agricultural'?'selected':''}>Agricultural / Open</option>
                        </select>
                    </div>
                    <div class="f-group">
                        <label class="f-label">Price / Assessed Value ($)</label>
                        <div class="f-row2">
                            <input class="f-input" type="number" placeholder="Min $" value="${filters.minPrice}" oninput="updateFilter('minPrice', this.value, false)">
                            <input class="f-input" type="number" placeholder="Max $" value="${filters.maxPrice}" oninput="updateFilter('maxPrice', this.value, false)">
                        </div>
                    </div>
                    <div class="f-group">
                        <label class="f-label">Lot Size (Acres)</label>
                        <div class="f-row2">
                            <input class="f-input" type="number" step="0.1" placeholder="Min AC" value="${filters.minAcres}" oninput="updateFilter('minAcres', this.value, false)">
                            <input class="f-input" type="number" step="0.1" placeholder="Max AC" value="${filters.maxAcres}" oninput="updateFilter('maxAcres', this.value, false)">
                        </div>
                    </div>
                    <div class="f-group">
                        <label class="f-label">Deed Owner Name</label>
                        <input class="f-input" type="text" placeholder="Search owner entity..." value="${filters.owner}" oninput="updateFilter('owner', this.value, false)">
                    </div>
                    <button class="btn-ghost" onclick="resetAllFilters()">Reset All Filters</button>
                `;
            } else if (activeTool === 'insights') {
                title.innerText = 'Area & Portfolio Insights';
                const owners = new Set();
                let totalAcres = 0, totalVal = 0;
                const catMap = {};
                filtered.forEach(p => {
                    if (p.owner_name) owners.add(p.owner_name);
                    if (p.lot_size_acres) totalAcres += Number(p.lot_size_acres);
                    totalVal += Number(p.price || p.tax_assessed_value || 0);
                    catMap[p.category] = (catMap[p.category] || 0) + 1;
                });
                const catHtml = Object.entries(catMap).sort((a,b) => b[1]-a[1]).map(([k,v]) => `
                    <div style="margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.76rem; margin-bottom:3px;">
                            <span>${k}</span><strong>${v.toLocaleString()}</strong>
                        </div>
                        <div style="height:6px; background:var(--bg-input); border-radius:99px; overflow:hidden;">
                            <div style="height:100%; width:${(v/Math.max(1,filtered.length)*100).toFixed(1)}%; background:${getCategoryColor(k)};"></div>
                        </div>
                    </div>
                `).join('');
                body.innerHTML = `
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                        <div class="sg-box"><div class="sg-v" style="color:var(--accent-cyan);">${filtered.length.toLocaleString()}</div><div class="sg-l">Properties</div></div>
                        <div class="sg-box"><div class="sg-v" style="color:var(--accent-teal);">${owners.size.toLocaleString()}</div><div class="sg-l">Unique Owners</div></div>
                        <div class="sg-box"><div class="sg-v" style="color:var(--accent-amber);">${Math.round(totalAcres).toLocaleString()}</div><div class="sg-l">Total Acres</div></div>
                        <div class="sg-box"><div class="sg-v" style="color:var(--accent-emerald);">$${(totalVal/1e9).toFixed(2)}B</div><div class="sg-l">Total Valuation</div></div>
                    </div>
                    <div class="f-label" style="margin-top:6px;">Breakdown by Land Use</div>
                    <div>${catHtml}</div>
                `;
            } else if (activeTool === 'following') {
                const savedList = ALL_PROPERTIES.filter(p => savedIds.has(p.id));
                title.innerText = `Saved Parcels (${savedList.length})`;
                if (savedList.length === 0) {
                    body.innerHTML = '<div style="color:var(--text-muted); font-size:0.82rem; text-align:center; padding:30px 10px;">Click any parcel on the map and press <strong>☆ SAVE PARCEL</strong> to bookmark it here.</div>';
                } else {
                    body.innerHTML = savedList.map(p => `
                        <div class="list-card" onclick="selectById(${p.id}, true)">
                            <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                                <span class="cat-pill">${p.category}</span>
                                <strong style="font-size:0.8rem; color:var(--accent-emerald);">${fmtMoney(p.price || p.tax_assessed_value)}</strong>
                            </div>
                            <div style="font-size:0.8rem; font-weight:700;">${p.address || p.title}</div>
                            <div style="font-size:0.7rem; color:var(--text-muted);">${p.city}, ${p.state} • ${p.lot_size_acres || '-'} AC</div>
                        </div>
                    `).join('');
                }
            } else if (activeTool === 'list') {
                title.innerText = `Matching List (${filtered.length.toLocaleString()})`;
                body.innerHTML = filtered.slice(0, 80).map(p => `
                    <div class="list-card" onclick="selectById(${p.id}, true)">
                        <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                            <span class="cat-pill">${p.category} • ${p.state}</span>
                            <strong style="font-size:0.8rem; color:var(--accent-emerald);">${fmtMoney(p.price || p.tax_assessed_value)}</strong>
                        </div>
                        <div style="font-size:0.8rem; font-weight:700;">${p.address || p.title}</div>
                        <div style="font-size:0.7rem; color:var(--text-muted);">${p.city || ''}${p.county ? ', ' + p.county : ''} • APN ${p.parcel_id || p.external_id}</div>
                    </div>
                `).join('') || '<div style="color:var(--text-muted); text-align:center; padding:24px;">No matching properties.</div>';
            } else if (activeTool === 'style') {
                title.innerText = 'Customize Map Boundaries';
                body.innerHTML = `
                    <div class="f-group">
                        <label class="f-label">Parcel Outline Color</label>
                        <select class="f-select" onchange="mapState.outlineColor=this.value; renderPolygonsAndLabels();">
                            <option value="auto" ${mapState.outlineColor==='auto'?'selected':''}>Auto (Yellow Satellite / Teal Street)</option>
                            <option value="#facc15" ${mapState.outlineColor==='#facc15'?'selected':''}>Classic Yellow</option>
                            <option value="#0f766e" ${mapState.outlineColor==='#0f766e'?'selected':''}>Deep Teal</option>
                            <option value="#38bdf8" ${mapState.outlineColor==='#38bdf8'?'selected':''}>Electric Cyan</option>
                            <option value="#ffffff" ${mapState.outlineColor==='#ffffff'?'selected':''}>Crisp White</option>
                        </select>
                    </div>
                    <div class="f-group">
                        <label class="f-label">Active Selection Highlight</label>
                        <select class="f-select" onchange="mapState.highlightColor=this.value; if(selectedProp) selectParcel(selectedProp, false);">
                            <option value="#ff2a7a" ${mapState.highlightColor==='#ff2a7a'?'selected':''}>Neon Pink</option>
                            <option value="#22d3ee" ${mapState.highlightColor==='#22d3ee'?'selected':''}>Bright Cyan</option>
                            <option value="#a3e635" ${mapState.highlightColor==='#a3e635'?'selected':''}>Lime Green</option>
                        </select>
                    </div>
                    <div class="f-group">
                        <label class="f-label">Border Thickness (${mapState.lineWeight}px)</label>
                        <input type="range" min="1" max="4" step="0.5" value="${mapState.lineWeight}" oninput="mapState.lineWeight=parseFloat(this.value); renderPolygonsAndLabels();">
                    </div>
                    <div class="f-group">
                        <label class="f-label">Parcel Fill Opacity (${Math.round(mapState.fillOpacity*100)}%)</label>
                        <input type="range" min="0" max="0.6" step="0.05" value="${mapState.fillOpacity}" oninput="mapState.fillOpacity=parseFloat(this.value); renderPolygonsAndLabels();">
                    </div>
                `;
            } else if (activeTool === 'export') {
                title.innerText = 'Export Filtered Data';
                body.innerHTML = `
                    <p style="font-size:0.8rem; color:var(--text-muted); line-height:1.45;">
                        Export the currently filtered <strong>${filtered.length.toLocaleString()}</strong> properties and parcel boundaries directly from the database.
                    </p>
                    <button class="btn-primary" onclick="exportGeoJSON()">⬇ Download GeoJSON (.geojson)</button>
                    <button class="btn-ghost" onclick="exportCSV()">⬇ Download Spreadsheet (.csv)</button>
                    <a href="/api/v1/geojson?limit=500" target="_blank" class="btn-ghost" style="text-align:center; text-decoration:none;">Open Live GeoJSON API ↗</a>
                `;
            }
        }

        // --- FILTER EXECUTION ---
        function updateFilter(key, val, flyToState) {
            filters[key] = val;
            applyAllFilters(flyToState);
        }

        function resetAllFilters() {
            Object.assign(filters, { search: '', category: 'all', status: 'all', state: 'all', city: '', zoning: 'all', owner: '', minPrice: '', maxPrice: '', minAcres: '', maxAcres: '' });
            document.getElementById('topSearchInput').value = '';
            document.getElementById('searchClearBtn').style.display = 'none';
            applyAllFilters(false);
            renderToolContent();
            resetUSAView();
        }

        function applyAllFilters(flyToState = false) {
            const s = filters.search.trim().toLowerCase();
            const cty = filters.city.trim().toLowerCase();
            const own = filters.owner.trim().toLowerCase();
            const minP = filters.minPrice !== '' ? parseFloat(filters.minPrice) : null;
            const maxP = filters.maxPrice !== '' ? parseFloat(filters.maxPrice) : null;
            const minA = filters.minAcres !== '' ? parseFloat(filters.minAcres) : null;
            const maxA = filters.maxAcres !== '' ? parseFloat(filters.maxAcres) : null;

            filtered = ALL_PROPERTIES.filter(p => {
                if (filters.category !== 'all' && p.category !== filters.category) return false;
                if (filters.status !== 'all' && p.listing_status !== filters.status) return false;
                if (filters.state !== 'all' && p.state !== filters.state) return false;
                if (cty && !`${p.city||''} ${p.county||''}`.toLowerCase().includes(cty)) return false;
                if (filters.zoning !== 'all' && !(p.zoning || '').toLowerCase().includes(filters.zoning.toLowerCase())) return false;
                if (own && !(p.owner_name || '').toLowerCase().includes(own)) return false;

                const val = p.price != null ? p.price : (p.tax_assessed_value || 0);
                if (minP !== null && val < minP) return false;
                if (maxP !== null && val > maxP) return false;
                if (minA !== null && (p.lot_size_acres || 0) < minA) return false;
                if (maxA !== null && (p.lot_size_acres || 0) > maxA) return false;

                if (s) {
                    const hay = `${p.address||''} ${p.city||''} ${p.county||''} ${p.state||''} ${p.zip_code||''} ${p.parcel_id||''} ${p.external_id||''} ${p.owner_name||''} ${p.title||''}`.toLowerCase();
                    if (!hay.includes(s)) return false;
                }
                return true;
            });

            document.getElementById('filterCountBadge').innerText = filtered.length.toLocaleString();
            document.getElementById('placeCount').innerText = `${filtered.length.toLocaleString()} marked`;
            if (filters.state !== 'all') {
                document.getElementById('placeLabel').innerText = `${filters.state} Parcels`;
            } else if (!selectedProp) {
                document.getElementById('placeLabel').innerText = 'United States (Nationwide)';
            }

            if (activeTool === 'filter') document.getElementById('toolPanelTitle').innerText = `Filters (${filtered.length.toLocaleString()} matches)`;
            else if (activeTool === 'list' || activeTool === 'insights') renderToolContent();

            renderClusters(filtered);
            renderPolygonsAndLabels();
            currentPage = 1;
            renderTableView();

            if (flyToState && filtered.length > 0) {
                const coords = filtered.filter(x => x.latitude && x.longitude).slice(0, 150).map(x => [x.latitude, x.longitude]);
                if (coords.length > 0) map.fitBounds(L.latLngBounds(coords), { padding: [60, 60], maxZoom: 12 });
            }
        }

        // --- SEARCH AUTOCOMPLETE ---
        function onTopSearch() {
            const val = document.getElementById('topSearchInput').value;
            document.getElementById('searchClearBtn').style.display = val ? 'block' : 'none';
            filters.search = val;
            applyAllFilters(false);

            const ac = document.getElementById('autocompleteBox');
            if (val.trim().length < 2 || filtered.length === 0) {
                ac.style.display = 'none';
                return;
            }
            ac.innerHTML = filtered.slice(0, 8).map(p => `
                <div class="ac-item" onclick="pickAC(${p.id})">
                    <span class="ac-title">${p.address || p.title}</span>
                    <span class="ac-sub">${p.category} • ${p.city || ''}, ${p.state || ''} • APN ${p.parcel_id || p.external_id}</span>
                </div>
            `).join('');
            ac.style.display = 'block';
        }

        function pickAC(id) {
            document.getElementById('autocompleteBox').style.display = 'none';
            selectById(id, true);
        }

        function clearSearch() {
            document.getElementById('topSearchInput').value = '';
            document.getElementById('searchClearBtn').style.display = 'none';
            document.getElementById('autocompleteBox').style.display = 'none';
            filters.search = '';
            applyAllFilters(false);
        }

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.top-search-wrap')) document.getElementById('autocompleteBox').style.display = 'none';
        });

        function selectById(id, fly = true) {
            const p = ALL_PROPERTIES.find(x => x.id === id);
            if (p) selectParcel(p, fly);
        }

        // --- LAYERS PANEL & OVERLAYS ---
        function toggleLayersPanel() {
            const lp = document.getElementById('layersPanel');
            const open = lp.classList.toggle('open');
            document.getElementById('layersBtn').classList.toggle('active', open);
        }

        function setBaseMap(key, cardEl) {
            if (mapState.base === key) return;
            map.removeLayer(baseLayers[mapState.base]);
            baseLayers[key].addTo(map);
            mapState.base = key;
            document.querySelectorAll('.layers-panel .l-card').forEach(c => {
                if (c.onclick && c.onclick.toString().includes('setBaseMap')) c.classList.remove('active');
            });
            cardEl.classList.add('active');
            renderPolygonsAndLabels();
        }

        function toggleMapLabel(mode, el) {
            const wasActive = mapState.labelMode === mode;
            mapState.labelMode = wasActive ? null : mode;
            ['lblOwnerCard', 'lblApnCard', 'lblAcresCard'].forEach(id => document.getElementById(id).classList.remove('active'));
            if (!wasActive) el.classList.add('active');
            renderPolygonsAndLabels();
        }

        function toggleOverlay(kind, el) {
            if (kind === 'outlines') {
                mapState.showOutlines = !mapState.showOutlines;
                el.classList.toggle('active', mapState.showOutlines);
            } else {
                const wasSame = mapState.overlayMode === kind;
                mapState.overlayMode = wasSame ? 'default' : kind;
                document.getElementById('ovZoningCard').classList.toggle('active', mapState.overlayMode === 'zoning');
                document.getElementById('ovValueCard').classList.toggle('active', mapState.overlayMode === 'value');
                updateLegend();
            }
            renderPolygonsAndLabels();
        }

        function updateLegend() {
            const leg = document.getElementById('overlayLegend');
            if (mapState.overlayMode === 'value') {
                leg.innerHTML = `
                    <span><span class="leg-dot" style="background:#34d399;"></span>Under $500K</span>
                    <span><span class="leg-dot" style="background:#fbbf24;"></span>$500K – $2M</span>
                    <span><span class="leg-dot" style="background:#f43f5e;"></span>$2M+ Valuation</span>
                    <span><span class="leg-dot" style="background:#ff2a7a;"></span>Selected</span>
                `;
            } else {
                leg.innerHTML = `
                    <span><span class="leg-dot" style="background:#38bdf8;"></span>Residential</span>
                    <span><span class="leg-dot" style="background:#fbbf24;"></span>Commercial</span>
                    <span><span class="leg-dot" style="background:#34d399;"></span>Land & Vacant</span>
                    <span><span class="leg-dot" style="background:#a78bfa;"></span>Industrial</span>
                    <span><span class="leg-dot" style="background:#ff2a7a;"></span>Selected Parcel</span>
                `;
            }
        }

        // --- MEASURE TOOL ---
        let measureActive = false;
        let measurePts = [];

        function toggleMeasure() {
            measureActive = !measureActive;
            document.getElementById('railMeasureBtn').classList.toggle('active', measureActive);
            document.getElementById('measureBanner').style.display = measureActive ? 'flex' : 'none';
            document.getElementById('map').style.cursor = measureActive ? 'crosshair' : '';
            if (!measureActive) clearMeasure();
        }

        function clearMeasure() {
            measurePts = [];
            measureLayer.clearLayers();
            document.getElementById('measureText').innerText = '📏 Click points on the map to measure distance & area';
        }

        map.on('click', (e) => {
            if (!measureActive) return;
            measurePts.push(e.latlng);
            measureLayer.clearLayers();
            measurePts.forEach(pt => L.circleMarker(pt, { radius: 5, color: '#ff2a7a', fillColor: '#fff', fillOpacity: 1, weight: 2 }).addTo(measureLayer));
            if (measurePts.length >= 2) {
                L.polyline(measurePts, { color: '#ff2a7a', weight: 3, dashArray: '5,5' }).addTo(measureLayer);
                let meters = 0;
                for (let i = 1; i < measurePts.length; i++) meters += measurePts[i-1].distanceTo(measurePts[i]);
                let txt = `📏 ${(meters*3.28084).toFixed(0)} ft (${(meters/1609.34).toFixed(2)} mi)`;
                if (measurePts.length >= 3) {
                    L.polygon(measurePts, { color: '#ff2a7a', fillColor: '#ff2a7a', fillOpacity: 0.2, weight: 2 }).addTo(measureLayer);
                    const R = 6378137; let area = 0;
                    for (let i = 0; i < measurePts.length; i++) {
                        const a = measurePts[i], b = measurePts[(i+1)%measurePts.length];
                        area += ((b.lng-a.lng)*Math.PI/180) * (2 + Math.sin(a.lat*Math.PI/180) + Math.sin(b.lat*Math.PI/180));
                    }
                    txt += ` | Area: ${(Math.abs(area*R*R/2)/4046.8564).toFixed(2)} AC`;
                }
                document.getElementById('measureText').innerText = txt;
            }
        });

        function resetUSAView() {
            closeParcelCard();
            document.getElementById('placeLabel').innerText = filters.state === 'all' ? 'United States (Nationwide)' : `${filters.state} Parcels`;
            map.flyTo([38.5, -96.5], 4, { duration: 0.85 });
        }

        function zoomToSampleLot() {
            const target = filtered.find(p => p.raw_data && p.raw_data.geojson_geometry) || filtered[0];
            if (target) selectParcel(target, true);
        }

        // --- EXPORTS ---
        function exportGeoJSON() {
            const fc = {
                type: 'FeatureCollection',
                features: filtered.filter(p => p.latitude && p.longitude).map(p => ({
                    type: 'Feature', id: p.id,
                    geometry: (p.raw_data && p.raw_data.geojson_geometry) || { type: 'Point', coordinates: [p.longitude, p.latitude] },
                    properties: { id: p.id, apn: p.parcel_id || p.external_id, category: p.category, address: p.address, city: p.city, county: p.county, state: p.state, price: p.price, tax_assessed_value: p.tax_assessed_value, lot_size_acres: p.lot_size_acres, owner_name: p.owner_name, zoning: p.zoning }
                }))
            };
            const a = document.createElement('a');
            a.href = URL.createObjectURL(new Blob([JSON.stringify(fc)], { type: 'application/geo+json' }));
            a.download = `parcels_${filters.state}_${filters.category}.geojson`;
            a.click();
        }

        function exportCSV() {
            const headers = ['id','apn','category','status','address','city','county','state','zip_code','price','tax_assessed_value','lot_size_acres','sqft','zoning','owner_name'];
            const lines = [headers.join(',')];
            filtered.forEach(p => {
                lines.push(headers.map(h => {
                    const val = h === 'apn' ? (p.parcel_id || p.external_id || '') : (h === 'status' ? (p.listing_status || '') : (p[h] ?? ''));
                    return `"${String(val).replace(/"/g, '""')}"`;
                }).join(','));
            });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' }));
            a.download = `parcels_${filters.state}.csv`;
            a.click();
        }

        // --- TABLE / GRID VIEW ---
        function switchMode(mode) {
            const isMap = mode === 'map';
            document.getElementById('mapView').style.display = isMap ? 'block' : 'none';
            document.getElementById('tableView').style.display = isMap ? 'none' : 'block';
            document.getElementById('btnMapMode').classList.toggle('active', isMap);
            document.getElementById('btnTableMode').classList.toggle('active', !isMap);
            if (isMap) setTimeout(() => map.invalidateSize(), 100);
            else renderTableView();
        }

        function renderTableView() {
            document.getElementById('tvMatchNum').innerText = filtered.length.toLocaleString();
            const totalAc = filtered.reduce((acc, p) => acc + (Number(p.lot_size_acres) || 0), 0);
            document.getElementById('tvAcresNum').innerText = Math.round(totalAc).toLocaleString() + ' AC';

            const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
            if (currentPage > pages) currentPage = pages;
            const items = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
            document.getElementById('tvPageLbl').innerText = `Page ${currentPage} of ${pages}`;
            document.getElementById('tvPrev').disabled = currentPage <= 1;
            document.getElementById('tvNext').disabled = currentPage >= pages;

            document.getElementById('tvGrid').innerHTML = items.map(p => `
                <div class="grid-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="cat-pill">${p.category}</span>
                        <span style="font-size:0.72rem; color:var(--text-muted); font-weight:700;">${p.state || 'US'}</span>
                    </div>
                    <div style="font-size:1.25rem; font-weight:800; color:var(--accent-emerald);">${p.price ? fmtMoney(p.price) : (p.lease_rate || fmtMoney(p.tax_assessed_value))}</div>
                    <div style="font-size:0.92rem; font-weight:700;">${p.address || p.title}</div>
                    <div style="font-size:0.78rem; color:var(--text-muted);">📍 ${p.city || ''}${p.county ? ', ' + p.county : ''}, ${p.state || ''}</div>
                    <div style="font-size:0.74rem; color:var(--text-muted); background:var(--bg-input); padding:7px 9px; border-radius:7px; border:1px solid var(--border);">
                        ${p.lot_size_acres ? `<strong>${p.lot_size_acres} AC</strong>` : ''} ${p.zoning ? `• ${p.zoning}` : ''} • APN ${p.parcel_id || p.external_id}
                    </div>
                    <button class="btn-primary" style="margin-top:auto;" onclick="switchMode('map'); setTimeout(()=>selectById(${p.id}, true), 120);">🗺️ Inspect on Map</button>
                </div>
            `).join('');
        }

        function changeGridPage(d) {
            currentPage += d;
            renderTableView();
            document.getElementById('tableView').scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function checkHealth() {
            try {
                const r = await fetch('/api/v1/health');
                if (r.ok) {
                    const d = await r.json();
                    const mode = d.database === 'PostgreSQL 16' ? 'PG 16 Live' : 'Cloud Store';
                    document.getElementById('apiStatusPill').innerHTML = `<span class="pulse-dot"></span> __TOTAL_COUNT__ (${mode}) • 50 States`;
                }
            } catch (e) {}
        }

        // Init
        document.getElementById('savedBadge').innerText = savedIds.size;
        renderToolContent();
        applyAllFilters(false);
        checkHealth();
    </script>
</body>
</html>
"""

    html_output = (
        html_template
        .replace("__TOTAL_COUNT__", f"{total_count:,}")
        .replace("__COMPACT_JSON__", compact_json)
    )

    out_file = Path(__file__).resolve().parent / "outputs" / "dashboard.html"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(html_output, encoding="utf-8")
    print(f"Generated ParcelScope US Unified Map UI with {total_count} marked parcels at {out_file} ({len(html_output)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    generate_web_dashboard()
