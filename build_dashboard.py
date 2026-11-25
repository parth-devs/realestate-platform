import json
from pathlib import Path
import psycopg2
from config import settings

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
            SELECT id, source, external_id, title, property_type, listing_status,
                   price, price_per_sqft, lease_rate, tax_assessed_value,
                   beds, baths, sqft, lot_size_acres, year_built,
                   address, city, county, state, zip_code, latitude, longitude,
                   parcel_id, owner_name, legal_description, zoning, url, broker_name,
                   raw_data
            FROM properties
            ORDER BY state, price DESC NULLS LAST;
        """)
        cols = [d[0] for d in cur.description]
        raw_rows = [dict(zip(cols, row)) for row in cur.fetchall()]

        cur.execute("SELECT source, COUNT(*) FROM properties GROUP BY source;")
        counts = dict(cur.fetchall())

        cur.execute("SELECT state, COUNT(*) FROM properties WHERE state IS NOT NULL GROUP BY state ORDER BY COUNT(*) DESC LIMIT 10;")
        top_states = [{"state": r[0], "count": r[1]} for r in cur.fetchall()]

    conn.close()

    # Clean & compact records for fast client-side rendering
    rows = []
    for r in raw_rows:
        cleaned = {}
        for k, v in r.items():
            if v is None:
                continue
            if hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
                cleaned[k] = float(v)
            else:
                cleaned[k] = v
        rows.append(cleaned)

    zillow_count = counts.get("zillow", 0)
    loopnet_count = counts.get("loopnet", 0)
    landglide_count = counts.get("landglide", 0) + counts.get("texas_cad", 0) + counts.get("us_parcels", 0)
    regrid_count = counts.get("regrid", 0)
    total_count = len(rows)

    compact_json = json.dumps(rows, separators=(",", ":"))
    top_states_json = json.dumps(top_states, separators=(",", ":"))

    html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoEstate Intelligence — Spatial US Real Estate & Parcel Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
    <!-- Leaflet & MarkerCluster -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <style>
        :root {
            --bg-dark: #070b14;
            --bg-panel: rgba(13, 19, 33, 0.90);
            --bg-card: #111827;
            --bg-elevated: #1a2438;
            --border: rgba(148, 163, 184, 0.16);
            --border-bright: rgba(56, 189, 248, 0.45);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-violet: #c084fc;
            --accent-pink: #ff2a7a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }

        /* Top Command Navbar */
        .topbar {
            height: 58px;
            background: rgba(9, 13, 24, 0.96);
            border-bottom: 1px solid var(--border);
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            z-index: 1200;
            flex-shrink: 0;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 800;
            font-size: 1.05rem;
            letter-spacing: -0.02em;
            white-space: nowrap;
        }
        .brand-logo {
            width: 32px; height: 32px; border-radius: 9px;
            background: linear-gradient(135deg, #0ea5e9, #a855f7);
            display: grid; place-items: center; font-size: 1rem;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
        }
        .pg-pill {
            font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 999px;
            background: rgba(52, 211, 153, 0.12); color: var(--accent-emerald);
            border: 1px solid rgba(52, 211, 153, 0.3);
            display: flex; align-items: center; gap: 5px;
        }
        .pulse-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent-emerald); box-shadow: 0 0 8px var(--accent-emerald); }

        .view-switcher {
            display: flex; background: #0f172a; padding: 4px; border-radius: 10px;
            border: 1px solid var(--border); gap: 4px;
        }
        .view-btn {
            border: none; background: transparent; color: var(--text-muted);
            padding: 6px 14px; border-radius: 7px; font-size: 0.82rem; font-weight: 600;
            cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px;
        }
        .view-btn.active {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.22), rgba(168, 85, 247, 0.22));
            color: #fff; border: 1px solid rgba(56, 189, 248, 0.35);
        }

        .top-actions { display: flex; align-items: center; gap: 8px; }
        .top-link {
            text-decoration: none; font-size: 0.78rem; font-weight: 600;
            padding: 6px 11px; border-radius: 7px; border: 1px solid var(--border);
            color: var(--text-muted); background: rgba(255,255,255,0.03);
            cursor: pointer; transition: all 0.18s; white-space: nowrap;
        }
        .top-link:hover { color: #fff; border-color: var(--accent-cyan); background: rgba(56, 189, 248, 0.1); }
        .top-link.primary { color: var(--accent-cyan); border-color: rgba(56, 189, 248, 0.35); }

        /* Main Stage */
        .workspace { position: relative; flex: 1; overflow: hidden; }

        /* Spatial Map View */
        #mapView { position: absolute; inset: 0; display: block; }
        #map { width: 100%; height: 100%; background: #060911; }

        /* Left Floating Spatial Dock */
        .left-dock {
            position: absolute; top: 14px; left: 14px; bottom: 14px; width: 370px;
            background: var(--bg-panel); backdrop-filter: blur(18px);
            border: 1px solid var(--border); border-radius: 16px;
            z-index: 1000; display: flex; flex-direction: column;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            transition: transform 0.25s ease;
            overflow: hidden;
        }
        .left-dock.collapsed { transform: translateX(-390px); }

        .dock-toggle-pill {
            position: absolute; top: 14px; left: 14px; z-index: 999;
            background: var(--bg-panel); backdrop-filter: blur(12px);
            border: 1px solid var(--border); color: #fff;
            padding: 9px 14px; border-radius: 10px; font-size: 0.82rem; font-weight: 600;
            cursor: pointer; display: none; box-shadow: 0 8px 24px rgba(0,0,0,0.45);
        }

        .dock-header {
            padding: 14px 16px 12px; border-bottom: 1px solid var(--border);
            display: flex; flex-direction: column; gap: 10px;
        }
        .dock-title-row { display: flex; justify-content: space-between; align-items: center; }
        .dock-title-row span { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
        .collapse-btn {
            background: rgba(255,255,255,0.06); border: 1px solid var(--border);
            color: var(--text-muted); border-radius: 6px; padding: 3px 8px; font-size: 0.75rem; cursor: pointer;
        }
        .collapse-btn:hover { color: #fff; }

        /* Search + Autocomplete */
        .search-wrap { position: relative; }
        .search-input {
            width: 100%; background: rgba(7, 11, 20, 0.85); border: 1px solid var(--border);
            border-radius: 10px; padding: 10px 34px 10px 12px; color: #fff;
            font-size: 0.86rem; outline: none; transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--accent-cyan); }
        .search-clear {
            position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
            background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1rem; display: none;
        }
        .autocomplete-box {
            position: absolute; top: calc(100% + 6px); left: 0; right: 0;
            background: #0f172a; border: 1px solid var(--border-bright); border-radius: 10px;
            max-height: 260px; overflow-y: auto; z-index: 1200; display: none;
            box-shadow: 0 14px 30px rgba(0,0,0,0.7);
        }
        .ac-item {
            padding: 9px 12px; border-bottom: 1px solid var(--border); cursor: pointer;
            display: flex; flex-direction: column; gap: 2px;
        }
        .ac-item:hover { background: rgba(56, 189, 248, 0.12); }
        .ac-title { font-size: 0.82rem; font-weight: 600; color: #fff; }
        .ac-sub { font-size: 0.72rem; color: var(--text-muted); }

        /* Filters inside Dock */
        .filter-chips { display: flex; flex-wrap: wrap; gap: 6px; }
        .chip {
            padding: 5px 9px; border-radius: 7px; font-size: 0.74rem; font-weight: 600;
            background: rgba(255,255,255,0.04); border: 1px solid var(--border);
            color: var(--text-muted); cursor: pointer; transition: all 0.16s;
        }
        .chip:hover { color: #fff; border-color: rgba(255,255,255,0.3); }
        .chip.active { background: rgba(56, 189, 248, 0.18); color: var(--accent-cyan); border-color: var(--accent-cyan); }
        .chip.active-regrid { background: rgba(192, 132, 252, 0.2); color: var(--accent-violet); border-color: var(--accent-violet); }
        .chip.active-land { background: rgba(52, 211, 153, 0.18); color: var(--accent-emerald); border-color: var(--accent-emerald); }
        .chip.active-loop { background: rgba(251, 191, 36, 0.18); color: var(--accent-amber); border-color: var(--accent-amber); }

        .filter-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .dark-select {
            width: 100%; background: rgba(7, 11, 20, 0.85); color: #fff;
            border: 1px solid var(--border); border-radius: 8px; padding: 7px 9px;
            font-size: 0.78rem; outline: none; cursor: pointer;
        }

        /* Spatial Tools Strip */
        .tools-strip {
            display: flex; gap: 6px; padding: 8px 16px;
            border-bottom: 1px solid var(--border); background: rgba(7, 11, 20, 0.45);
        }
        .tool-btn {
            flex: 1; padding: 6px 8px; border-radius: 7px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.03); color: var(--text-muted);
            font-size: 0.73rem; font-weight: 600; cursor: pointer; transition: all 0.15s;
            display: flex; align-items: center; justify-content: center; gap: 4px;
        }
        .tool-btn:hover { color: #fff; border-color: var(--accent-cyan); }
        .tool-btn.active { background: rgba(255, 42, 122, 0.2); color: #ff7ab0; border-color: var(--accent-pink); }

        /* Sidebar Results List */
        .dock-list-header {
            padding: 8px 16px; font-size: 0.74rem; color: var(--text-muted);
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--border);
        }
        .dock-list { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 6px; }
        .mini-item {
            background: rgba(255,255,255,0.03); border: 1px solid var(--border);
            border-radius: 10px; padding: 10px 12px; cursor: pointer; transition: all 0.16s;
        }
        .mini-item:hover, .mini-item.selected {
            background: rgba(56, 189, 248, 0.1); border-color: var(--accent-cyan);
        }
        .mini-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .mini-badge { font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; }
        .b-zillow { background: rgba(56, 189, 248, 0.18); color: var(--accent-cyan); }
        .b-loopnet { background: rgba(251, 191, 36, 0.18); color: var(--accent-amber); }
        .b-land { background: rgba(52, 211, 153, 0.18); color: var(--accent-emerald); }
        .b-regrid { background: rgba(192, 132, 252, 0.2); color: var(--accent-violet); }
        .mini-price { font-size: 0.85rem; font-weight: 800; color: var(--accent-emerald); }
        .mini-title { font-size: 0.8rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mini-sub { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; }

        /* Right Floating Parcel Inspector Drawer */
        .inspector-drawer {
            position: absolute; top: 14px; right: 14px; bottom: 72px; width: 390px;
            background: var(--bg-panel); backdrop-filter: blur(20px);
            border: 1px solid var(--border-bright); border-radius: 16px;
            z-index: 1100; display: flex; flex-direction: column;
            box-shadow: 0 24px 60px rgba(0,0,0,0.75);
            transform: translateX(420px); transition: transform 0.26s cubic-bezier(0.16, 1, 0.3, 1);
            overflow: hidden;
        }
        .inspector-drawer.open { transform: translateX(0); }

        .insp-header {
            padding: 16px 18px; border-bottom: 1px solid var(--border);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(192, 132, 252, 0.08));
            position: relative;
        }
        .insp-close {
            position: absolute; top: 14px; right: 14px; width: 28px; height: 28px;
            border-radius: 50%; border: 1px solid var(--border); background: rgba(0,0,0,0.35);
            color: #fff; cursor: pointer; font-size: 1rem; display: grid; place-items: center;
        }
        .insp-title { font-size: 1rem; font-weight: 700; margin: 8px 28px 4px 0; line-height: 1.3; }
        .insp-price { font-size: 1.45rem; font-weight: 800; color: var(--accent-emerald); }

        .insp-body { flex: 1; overflow-y: auto; padding: 14px 18px; display: flex; flex-direction: column; gap: 14px; }
        .stat-tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
        .stat-tile {
            background: rgba(7, 11, 20, 0.7); border: 1px solid var(--border);
            border-radius: 10px; padding: 8px 10px; text-align: center;
        }
        .stat-tile-val { font-size: 0.92rem; font-weight: 700; color: #fff; }
        .stat-tile-lbl { font-size: 0.66rem; color: var(--text-muted); text-transform: uppercase; margin-top: 2px; }

        .insp-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        .insp-table td { padding: 8px 4px; border-bottom: 1px solid var(--border); vertical-align: top; }
        .insp-table td:first-child { color: var(--text-muted); width: 42%; font-weight: 500; }
        .insp-table td:last-child { color: #fff; font-weight: 600; text-align: right; word-break: break-word; }

        .geojson-box {
            background: #060911; border: 1px solid var(--border); border-radius: 8px;
            padding: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
            color: var(--accent-violet); max-height: 110px; overflow-y: auto;
        }

        .insp-footer {
            padding: 12px 16px; border-top: 1px solid var(--border);
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: rgba(7,11,20,0.6);
        }
        .btn-action {
            padding: 9px 10px; border-radius: 8px; font-size: 0.78rem; font-weight: 600;
            text-align: center; text-decoration: none; cursor: pointer; border: 1px solid var(--border);
            background: rgba(255,255,255,0.05); color: #fff; transition: all 0.16s;
        }
        .btn-action:hover { border-color: var(--accent-cyan); background: rgba(56, 189, 248, 0.15); }
        .btn-action.highlight { background: linear-gradient(135deg, #0ea5e9, #8b5cf6); border: none; }

        /* Map Floating Layer Switcher + Measure Banner */
        .layer-switcher {
            position: absolute; bottom: 20px; right: 14px; z-index: 1000;
            background: var(--bg-panel); backdrop-filter: blur(14px);
            border: 1px solid var(--border); border-radius: 12px; padding: 5px;
            display: flex; gap: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .layer-opt {
            padding: 6px 11px; border-radius: 8px; border: none; background: transparent;
            color: var(--text-muted); font-size: 0.75rem; font-weight: 600; cursor: pointer;
        }
        .layer-opt.active { background: rgba(56, 189, 248, 0.22); color: #fff; }

        .measure-banner {
            position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
            z-index: 1150; background: rgba(15, 23, 42, 0.94); border: 1px solid var(--accent-pink);
            color: #fff; padding: 9px 16px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
            display: none; align-items: center; gap: 12px; box-shadow: 0 10px 30px rgba(255, 42, 122, 0.3);
        }

        /* Map Legend Pill */
        .map-legend {
            position: absolute; bottom: 20px; left: 400px; z-index: 990;
            background: var(--bg-panel); backdrop-filter: blur(12px);
            border: 1px solid var(--border); border-radius: 999px;
            padding: 6px 14px; display: flex; gap: 14px; font-size: 0.73rem; color: var(--text-muted);
        }
        .leg-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }

        /* Analytics & Grid View */
        #gridView {
            position: absolute; inset: 0; overflow-y: auto; padding: 24px 28px;
            background: var(--bg-dark); display: none;
        }
        .grid-container { max-width: 1440px; margin: 0 auto; }

        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr)); gap: 14px; margin-bottom: 22px; }
        .kpi-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
            padding: 16px 18px; display: flex; flex-direction: column; gap: 5px;
        }
        .kpi-label { font-size: 0.74rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .kpi-val { font-size: 1.65rem; font-weight: 800; }

        .analytics-strip {
            display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 22px;
        }
        .analytics-box {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 18px;
        }
        .analytics-box h3 { font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 12px; }
        .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.8rem; }
        .bar-lbl { width: 95px; color: var(--text-muted); font-weight: 600; }
        .bar-track { flex: 1; height: 8px; background: #070b14; border-radius: 99px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 99px; }
        .bar-num { width: 55px; text-align: right; font-weight: 700; }

        .grid-controls {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
            padding: 14px 18px; margin-bottom: 20px; display: flex; flex-wrap: wrap;
            justify-content: space-between; align-items: center; gap: 12px;
        }
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 16px; }
        .prop-card {
            background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
            padding: 16px; display: flex; flex-direction: column; gap: 8px; transition: border-color 0.18s;
        }
        .prop-card:hover { border-color: var(--accent-cyan); }
        .card-actions { display: flex; gap: 8px; margin-top: auto; padding-top: 8px; }
        .card-btn {
            flex: 1; padding: 7px; border-radius: 7px; border: 1px solid var(--border);
            background: rgba(255,255,255,0.04); color: #fff; font-size: 0.76rem; font-weight: 600; cursor: pointer;
        }
        .card-btn:hover { border-color: var(--accent-cyan); background: rgba(56, 189, 248, 0.12); }

        .pagination-bar {
            display: flex; justify-content: center; align-items: center; gap: 12px;
            margin-top: 24px; padding-bottom: 30px;
        }
        .page-btn {
            padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border);
            background: var(--bg-card); color: #fff; font-size: 0.82rem; font-weight: 600; cursor: pointer;
        }
        .page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        /* Custom Leaflet Cluster Dark Style */
        .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {
            background-color: rgba(56, 189, 248, 0.25) !important;
        }
        .marker-cluster-small div, .marker-cluster-medium div, .marker-cluster-large div {
            background-color: rgba(14, 165, 233, 0.9) !important;
            color: #fff !important; font-weight: 700 !important; font-family: 'Inter', sans-serif !important;
        }

        @media (max-width: 900px) {
            .left-dock { width: calc(100% - 28px); height: 48%; top: auto; }
            .inspector-drawer { width: calc(100% - 28px); }
            .map-legend { display: none; }
            .analytics-strip { grid-template-columns: 1fr; }
            .top-actions { display: none; }
        }
    </style>
</head>
<body>

    <!-- Top Navigation Bar -->
    <header class="topbar">
        <div class="brand">
            <div class="brand-logo">🛰️</div>
            <span>GeoEstate Intelligence</span>
            <span class="pg-pill"><span class="pulse-dot"></span> __TOTAL_COUNT__ PG Assets • 50 States</span>
        </div>

        <div class="view-switcher">
            <button class="view-btn active" id="btnMapView" onclick="switchView('map')">🛰️ Spatial Map Explorer</button>
            <button class="view-btn" id="btnGridView" onclick="switchView('grid')">📊 Analytics & Grid View</button>
        </div>

        <div class="top-actions">
            <button class="top-link" onclick="exportFilteredGeoJSON()">⬇ GeoJSON</button>
            <a href="/api/v1/geojson?limit=200" target="_blank" class="top-link">GeoJSON API ↗</a>
            <a href="/api/v1/regrid" target="_blank" class="top-link">Regrid API ↗</a>
            <a href="/docs" target="_blank" class="top-link primary">Swagger Docs ↗</a>
        </div>
    </header>

    <div class="workspace">

        <!-- VIEW 1: SPATIAL MAP EXPLORER -->
        <div id="mapView">
            <div id="map"></div>

            <!-- Measurement Banner -->
            <div class="measure-banner" id="measureBanner">
                <span id="measureText">📏 Click points on the satellite map to measure distance & area</span>
                <button class="collapse-btn" onclick="clearMeasure()">Clear</button>
                <button class="collapse-btn" onclick="toggleMeasureMode()">Done</button>
            </div>

            <!-- Collapsed Sidebar Re-Open Pill -->
            <button class="dock-toggle-pill" id="dockOpenBtn" onclick="toggleDock(false)">☰ Explorer & Filters (<span id="pillFilteredCount">__TOTAL_COUNT__</span>)</button>

            <!-- Left Command Dock -->
            <aside class="left-dock" id="leftDock">
                <div class="dock-header">
                    <div class="dock-title-row">
                        <span>Spatial Explorer & Filters</span>
                        <button class="collapse-btn" onclick="toggleDock(true)">Hide ◀</button>
                    </div>

                    <!-- Search with Autocomplete -->
                    <div class="search-wrap">
                        <input type="text" id="searchInput" class="search-input" placeholder="Search address, city, APN, owner, zip..." oninput="onSearchInput()" autocomplete="off">
                        <button class="search-clear" id="searchClearBtn" onclick="clearSearch()">&times;</button>
                        <div class="autocomplete-box" id="autocompleteBox"></div>
                    </div>

                    <!-- Platform Filter Chips -->
                    <div class="filter-chips">
                        <button class="chip active" data-src="all" onclick="setSource('all', this)">All (__TOTAL_COUNT__)</button>
                        <button class="chip" data-src="regrid" onclick="setSource('regrid', this)">🌐 Regrid (__REGRID_COUNT__)</button>
                        <button class="chip" data-src="us_parcels" onclick="setSource('us_parcels', this)">🗺️ LandGlide (__LAND_COUNT__)</button>
                        <button class="chip" data-src="zillow" onclick="setSource('zillow', this)">🏡 Zillow (__ZILLOW_COUNT__)</button>
                        <button class="chip" data-src="loopnet" onclick="setSource('loopnet', this)">🏢 LoopNet (__LOOPNET_COUNT__)</button>
                    </div>

                    <!-- State & Min Size Filters -->
                    <div class="filter-row">
                        <select id="stateFilter" class="dark-select" onchange="applyFilters(true)">
                            <option value="all">All 50 US States</option>
                            <option value="AL">Alabama (AL)</option><option value="AK">Alaska (AK)</option>
                            <option value="AZ">Arizona (AZ)</option><option value="AR">Arkansas (AR)</option>
                            <option value="CA">California (CA)</option><option value="CO">Colorado (CO)</option>
                            <option value="CT">Connecticut (CT)</option><option value="DE">Delaware (DE)</option>
                            <option value="FL">Florida (FL)</option><option value="GA">Georgia (GA)</option>
                            <option value="HI">Hawaii (HI)</option><option value="ID">Idaho (ID)</option>
                            <option value="IL">Illinois (IL)</option><option value="IN">Indiana (IN)</option>
                            <option value="IA">Iowa (IA)</option><option value="KS">Kansas (KS)</option>
                            <option value="KY">Kentucky (KY)</option><option value="LA">Louisiana (LA)</option>
                            <option value="ME">Maine (ME)</option><option value="MD">Maryland (MD)</option>
                            <option value="MA">Massachusetts (MA)</option><option value="MI">Michigan (MI)</option>
                            <option value="MN">Minnesota (MN)</option><option value="MS">Mississippi (MS)</option>
                            <option value="MO">Missouri (MO)</option><option value="MT">Montana (MT)</option>
                            <option value="NE">Nebraska (NE)</option><option value="NV">Nevada (NV)</option>
                            <option value="NH">New Hampshire (NH)</option><option value="NJ">New Jersey (NJ)</option>
                            <option value="NM">New Mexico (NM)</option><option value="NY">New York (NY)</option>
                            <option value="NC">North Carolina (NC)</option><option value="ND">North Dakota (ND)</option>
                            <option value="OH">Ohio (OH)</option><option value="OK">Oklahoma (OK)</option>
                            <option value="OR">Oregon (OR)</option><option value="PA">Pennsylvania (PA)</option>
                            <option value="RI">Rhode Island (RI)</option><option value="SC">South Carolina (SC)</option>
                            <option value="SD">South Dakota (SD)</option><option value="TN">Tennessee (TN)</option>
                            <option value="TX">Texas (TX)</option><option value="UT">Utah (UT)</option>
                            <option value="VT">Vermont (VT)</option><option value="VA">Virginia (VA)</option>
                            <option value="WA">Washington (WA)</option><option value="WV">West Virginia (WV)</option>
                            <option value="WI">Wisconsin (WI)</option><option value="WY">Wyoming (WY)</option>
                        </select>

                        <select id="acreFilter" class="dark-select" onchange="applyFilters(false)">
                            <option value="0">Any Lot Size</option>
                            <option value="1">1+ Acres</option>
                            <option value="5">5+ Acres</option>
                            <option value="10">10+ Acres</option>
                            <option value="20">20+ Acres</option>
                        </select>
                    </div>
                </div>

                <!-- Spatial Tools -->
                <div class="tools-strip">
                    <button class="tool-btn" id="measureBtn" onclick="toggleMeasureMode()">📏 Measure</button>
                    <button class="tool-btn" onclick="resetUSAView()">🎯 USA View</button>
                    <button class="tool-btn" onclick="zoomToPolygonsDemo()">🔍 Zoom Parcel</button>
                </div>

                <!-- Matching List Header -->
                <div class="dock-list-header">
                    <span>Matching Properties</span>
                    <strong style="color: #fff;" id="dockMatchCount">__TOTAL_COUNT__</strong>
                </div>

                <!-- Scrollable Preview List -->
                <div class="dock-list" id="dockList"></div>
            </aside>

            <!-- Map Legend -->
            <div class="map-legend">
                <span><span class="leg-dot" style="background: var(--accent-violet);"></span>Regrid Parcels</span>
                <span><span class="leg-dot" style="background: var(--accent-emerald);"></span>LandGlide CAD</span>
                <span><span class="leg-dot" style="background: var(--accent-cyan);"></span>Zillow Homes</span>
                <span><span class="leg-dot" style="background: var(--accent-amber);"></span>LoopNet Commercial</span>
                <span><span class="leg-dot" style="background: var(--accent-pink);"></span>Selected</span>
            </div>

            <!-- Base Layer Switcher -->
            <div class="layer-switcher">
                <button class="layer-opt active" onclick="setBaseMap('satellite', this)">🛰️ Esri Satellite</button>
                <button class="layer-opt" onclick="setBaseMap('dark', this)">🌑 Dark Vector</button>
                <button class="layer-opt" onclick="setBaseMap('street', this)">🗺️ Streets</button>
            </div>

            <!-- Right Property & Parcel Inspector Drawer -->
            <aside class="inspector-drawer" id="inspectorDrawer">
                <div class="insp-header">
                    <button class="insp-close" onclick="closeInspector()">&times;</button>
                    <div id="inspBadges" style="display:flex; gap:6px; align-items:center;"></div>
                    <h2 class="insp-title" id="inspTitle">Property Details</h2>
                    <div class="insp-price" id="inspPrice">$0</div>
                </div>
                <div class="insp-body">
                    <div class="stat-tiles" id="inspStatTiles"></div>
                    <table class="insp-table" id="inspTable"></table>
                    <div id="inspGeoSection" style="display:none;">
                        <div style="font-size:0.74rem; color:var(--text-muted); font-weight:600; margin-bottom:6px; display:flex; justify-content:space-between;">
                            <span>GIS POLYGON BOUNDARY (GEOJSON)</span>
                            <a href="#" onclick="copySelectedGeoJSON(event)" style="color:var(--accent-cyan); text-decoration:none;">Copy JSON</a>
                        </div>
                        <div class="geojson-box" id="inspGeoBox"></div>
                    </div>
                </div>
                <div class="insp-footer">
                    <a href="#" id="inspApiLink" target="_blank" class="btn-action">PG API JSON ↗</a>
                    <a href="#" id="inspSourceLink" target="_blank" class="btn-action highlight">Open Listing ↗</a>
                </div>
            </aside>
        </div>

        <!-- VIEW 2: ANALYTICS & GRID VIEW -->
        <div id="gridView">
            <div class="grid-container">
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <span class="kpi-label">Total PostgreSQL Assets</span>
                        <span class="kpi-val" style="color: var(--accent-cyan);">__TOTAL_COUNT__</span>
                    </div>
                    <div class="kpi-card">
                        <span class="kpi-label">Zillow Residential</span>
                        <span class="kpi-val" style="color: var(--accent-cyan);">__ZILLOW_COUNT__</span>
                    </div>
                    <div class="kpi-card">
                        <span class="kpi-label">LoopNet Commercial</span>
                        <span class="kpi-val" style="color: var(--accent-amber);">__LOOPNET_COUNT__</span>
                    </div>
                    <div class="kpi-card">
                        <span class="kpi-label">LandGlide / CAD</span>
                        <span class="kpi-val" style="color: var(--accent-emerald);">__LAND_COUNT__</span>
                    </div>
                    <div class="kpi-card">
                        <span class="kpi-label">Regrid Parcels</span>
                        <span class="kpi-val" style="color: var(--accent-violet);">__REGRID_COUNT__</span>
                    </div>
                    <div class="kpi-card">
                        <span class="kpi-label">Coverage Scope</span>
                        <span class="kpi-val" style="color: #fff;">50 States</span>
                    </div>
                </div>

                <div class="analytics-strip">
                    <div class="analytics-box">
                        <h3>Platform Distribution (Live PG)</h3>
                        <div id="sourceBars"></div>
                    </div>
                    <div class="analytics-box">
                        <h3>Top US States by Asset Volume</h3>
                        <div id="stateBars"></div>
                    </div>
                </div>

                <div class="grid-controls">
                    <div style="font-size:0.9rem; font-weight:700;">
                        Showing <span id="gridShowingCount" style="color:var(--accent-cyan);">0</span> matching records
                    </div>
                    <div style="display:flex; gap:10px; align-items:center;">
                        <button class="page-btn" onclick="switchView('map')">🛰️ Open Map View</button>
                        <button class="page-btn" onclick="exportFilteredGeoJSON()">⬇ Download GeoJSON</button>
                    </div>
                </div>

                <div class="cards-grid" id="cardsGrid"></div>

                <div class="pagination-bar">
                    <button class="page-btn" id="prevPageBtn" onclick="changePage(-1)">← Previous</button>
                    <span style="font-size:0.85rem; color:var(--text-muted);" id="pageIndicator">Page 1</span>
                    <button class="page-btn" id="nextPageBtn" onclick="changePage(1)">Next →</button>
                </div>
            </div>
        </div>

    </div>

    <script>
        const ALL_PROPERTIES = __COMPACT_JSON__;
        const TOP_STATES = __TOP_STATES_JSON__;

        let filteredProperties = ALL_PROPERTIES;
        let activeSource = 'all';
        let selectedProperty = null;
        let currentPage = 1;
        const PAGE_SIZE = 48;

        // --- MAP INITIALIZATION ---
        const map = L.map('map', {
            center: [38.5, -96.5],
            zoom: 4,
            zoomControl: false,
            preferCanvas: true
        });
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        const baseLayers = {
            satellite: L.layerGroup([
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19, attribution: 'Powered by Esri'
                }),
                L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19
                })
            ]),
            dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                maxZoom: 19, attribution: '&copy; CARTO & OpenStreetMap'
            }),
            street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19, attribution: '&copy; OpenStreetMap'
            })
        };
        let activeBaseKey = 'satellite';
        baseLayers.satellite.addTo(map);

        function setBaseMap(key, btn) {
            if (activeBaseKey === key) return;
            map.removeLayer(baseLayers[activeBaseKey]);
            baseLayers[key].addTo(map);
            activeBaseKey = key;
            document.querySelectorAll('.layer-opt').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        // Cluster + Parcel Polygon Layers
        const clusterGroup = L.markerClusterGroup({
            chunkedLoading: true,
            maxClusterRadius: 48,
            disableClusteringAtZoom: 14
        });
        map.addLayer(clusterGroup);

        const parcelPolygonsLayer = L.layerGroup().addTo(map);
        const selectedHighlightLayer = L.layerGroup().addTo(map);

        function getSourceColor(src) {
            if (src === 'regrid') return '#c084fc';
            if (src === 'zillow') return '#38bdf8';
            if (src === 'loopnet') return '#fbbf24';
            return '#34d399';
        }

        function getSourceLabel(src) {
            if (src === 'regrid') return 'Regrid';
            if (src === 'zillow') return 'Zillow';
            if (src === 'loopnet') return 'LoopNet';
            return 'LandGlide';
        }

        function getBadgeClass(src) {
            if (src === 'regrid') return 'b-regrid';
            if (src === 'zillow') return 'b-zillow';
            if (src === 'loopnet') return 'b-loopnet';
            return 'b-land';
        }

        function formatMoney(v) {
            if (v === null || v === undefined) return 'Off-Market';
            return '$' + Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 });
        }

        function getDisplayPrice(p) {
            if (p.price) return formatMoney(p.price);
            if (p.lease_rate) return p.lease_rate;
            if (p.tax_assessed_value) return 'Assessed ' + formatMoney(p.tax_assessed_value);
            return 'Off-Market';
        }

        // Render Markers into Cluster Group
        function renderMapMarkers(items) {
            clusterGroup.clearLayers();
            const markers = [];

            for (let i = 0; i < items.length; i++) {
                const p = items[i];
                if (p.latitude == null || p.longitude == null) continue;
                const color = getSourceColor(p.source);
                const marker = L.circleMarker([p.latitude, p.longitude], {
                    radius: 6.5,
                    color: '#070b14',
                    weight: 1.5,
                    fillColor: color,
                    fillOpacity: 0.9
                });
                marker.on('click', () => {
                    if (!measureMode) selectProperty(p, false);
                });
                markers.push(marker);
            }
            clusterGroup.addLayers(markers);
        }

        // Draw GeoJSON Parcel Boundaries when zoomed in (>= 12)
        function renderVisiblePolygons() {
            parcelPolygonsLayer.clearLayers();
            if (map.getZoom() < 12) return;

            const bounds = map.getBounds();
            let drawn = 0;
            for (let i = 0; i < filteredProperties.length; i++) {
                const p = filteredProperties[i];
                if (p.latitude == null || p.longitude == null) continue;
                if (!bounds.contains([p.latitude, p.longitude])) continue;
                const geom = p.raw_data && p.raw_data.geojson_geometry;
                if (!geom) continue;

                const isRegrid = p.source === 'regrid';
                const strokeColor = isRegrid ? '#facc15' : '#34d399';
                const layer = L.geoJSON(geom, {
                    style: {
                        color: strokeColor,
                        weight: 1.8,
                        fillColor: strokeColor,
                        fillOpacity: 0.14
                    }
                });
                layer.on('click', () => {
                    if (!measureMode) selectProperty(p, false);
                });
                parcelPolygonsLayer.addLayer(layer);
                drawn++;
                if (drawn >= 350) break;
            }
        }
        map.on('moveend zoomend', renderVisiblePolygons);

        // Select & Highlight Property/Parcel + Open Right Inspector
        function selectProperty(p, shouldFly = true) {
            selectedProperty = p;
            selectedHighlightLayer.clearLayers();

            if (p.latitude != null && p.longitude != null) {
                if (shouldFly) {
                    map.flyTo([p.latitude, p.longitude], 16, { duration: 0.9 });
                }

                const geom = p.raw_data && p.raw_data.geojson_geometry;
                if (geom) {
                    L.geoJSON(geom, {
                        style: {
                            color: '#ff2a7a',
                            weight: 4,
                            fillColor: '#ff2a7a',
                            fillOpacity: 0.32
                        }
                    }).addTo(selectedHighlightLayer);
                } else {
                    L.circleMarker([p.latitude, p.longitude], {
                        radius: 13,
                        color: '#ff2a7a',
                        weight: 3.5,
                        fillColor: '#ff2a7a',
                        fillOpacity: 0.35
                    }).addTo(selectedHighlightLayer);
                }
            }

            openInspector(p);
        }

        function openInspector(p) {
            const rd = p.raw_data || {};
            document.getElementById('inspBadges').innerHTML = `
                <span class="mini-badge ${getBadgeClass(p.source)}">${getSourceLabel(p.source)}</span>
                <span class="mini-badge" style="background:rgba(255,255,255,0.08); color:#fff;">${p.state || 'US'}</span>
                <span style="font-size:0.72rem; color:var(--text-muted); font-family:'JetBrains Mono',monospace;">#${p.id}</span>
            `;
            document.getElementById('inspTitle').innerText = p.address ? `${p.address}, ${p.city || ''}` : (p.title || 'Property Asset');
            document.getElementById('inspPrice').innerText = getDisplayPrice(p);

            document.getElementById('inspStatTiles').innerHTML = `
                <div class="stat-tile">
                    <div class="stat-tile-val">${p.lot_size_acres ? p.lot_size_acres + ' AC' : '-'}</div>
                    <div class="stat-tile-lbl">Lot Size</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-tile-val">${p.sqft ? p.sqft.toLocaleString() : '-'}</div>
                    <div class="stat-tile-lbl">Bldg SqFt</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-tile-val">${p.beds ? p.beds + ' / ' + (p.baths || '-') : (p.zoning ? p.zoning.split(' ')[0] : 'N/A')}</div>
                    <div class="stat-tile-lbl">${p.beds ? 'Beds / Baths' : 'Zoning'}</div>
                </div>
            `;

            let rowsHtml = `
                <tr><td>External / APN ID</td><td>${p.external_id || '-'}</td></tr>
                <tr><td>Property Type</td><td>${p.property_type || '-'} (${p.listing_status || 'active'})</td></tr>
                <tr><td>County / State</td><td>${p.county || '-'}, ${p.state || '-'} ${p.zip_code || ''}</td></tr>
                <tr><td>Registered Owner</td><td>${p.owner_name || 'N/A'}</td></tr>
                <tr><td>County Tax Assessed</td><td>${p.tax_assessed_value ? formatMoney(p.tax_assessed_value) : '-'}</td></tr>
                <tr><td>Zoning</td><td>${p.zoning || '-'}</td></tr>
                <tr><td>Legal Description</td><td>${p.legal_description || '-'}</td></tr>
                <tr><td>GPS Coordinates</td><td>${p.latitude ? p.latitude + ', ' + p.longitude : '-'}</td></tr>
            `;

            if (p.source === 'regrid') {
                rowsHtml += `
                    <tr><td>Regrid UUID</td><td style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;">${rd.ll_uuid || '-'}</td></tr>
                    <tr><td>Owner Mailing</td><td>${rd.owner_mailing || '-'}</td></tr>
                    <tr><td>Land / Improvement</td><td>${formatMoney(rd.land_value)} / ${formatMoney(rd.improvement_value)}</td></tr>
                    <tr><td>Annual Tax (${rd.tax_year || 2025})</td><td>${formatMoney(rd.tax_amount)}</td></tr>
                    <tr><td>Last Deed Sale</td><td>${formatMoney(rd.last_sale_price)} (${rd.last_sale_date || '-'})</td></tr>
                `;
            } else if (p.broker_name) {
                rowsHtml += `<tr><td>Broker / Source</td><td>${p.broker_name}</td></tr>`;
            }

            document.getElementById('inspTable').innerHTML = rowsHtml;

            const geoSec = document.getElementById('inspGeoSection');
            if (rd.geojson_geometry) {
                geoSec.style.display = 'block';
                document.getElementById('inspGeoBox').innerText = JSON.stringify(rd.geojson_geometry, null, 2);
            } else {
                geoSec.style.display = 'none';
            }

            document.getElementById('inspApiLink').href = `/api/v1/properties/${p.id}`;
            const srcLink = document.getElementById('inspSourceLink');
            if (p.url) {
                srcLink.href = p.url;
                srcLink.style.display = 'block';
            } else {
                srcLink.style.display = 'none';
            }

            document.getElementById('inspectorDrawer').classList.add('open');
        }

        function closeInspector() {
            document.getElementById('inspectorDrawer').classList.remove('open');
            selectedHighlightLayer.clearLayers();
        }

        function copySelectedGeoJSON(e) {
            e.preventDefault();
            if (!selectedProperty || !selectedProperty.raw_data || !selectedProperty.raw_data.geojson_geometry) return;
            navigator.clipboard.writeText(JSON.stringify(selectedProperty.raw_data.geojson_geometry, null, 2));
            e.target.innerText = 'Copied ✓';
            setTimeout(() => e.target.innerText = 'Copy JSON', 1500);
        }

        // --- FILTERING & SEARCH ---
        function setSource(src, el) {
            activeSource = src;
            document.querySelectorAll('.chip').forEach(c => {
                c.className = 'chip';
            });
            if (src === 'regrid') el.classList.add('active-regrid');
            else if (src === 'us_parcels') el.classList.add('active-land');
            else if (src === 'loopnet') el.classList.add('active-loop');
            else el.classList.add('active');

            applyFilters(false);
        }

        function applyFilters(fitStateBounds = false) {
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            const state = document.getElementById('stateFilter').value;
            const minAcres = parseFloat(document.getElementById('acreFilter').value) || 0;

            filteredProperties = ALL_PROPERTIES.filter(p => {
                if (activeSource !== 'all') {
                    if (activeSource === 'us_parcels') {
                        if (!['us_parcels', 'texas_cad', 'landglide'].includes(p.source)) return false;
                    } else if (p.source !== activeSource) {
                        return false;
                    }
                }
                if (state !== 'all' && p.state !== state) return false;
                if (minAcres > 0 && (p.lot_size_acres || 0) < minAcres) return false;
                if (query) {
                    const hay = `${p.address || ''} ${p.city || ''} ${p.county || ''} ${p.state || ''} ${p.owner_name || ''} ${p.external_id || ''} ${p.title || ''}`.toLowerCase();
                    if (!hay.includes(query)) return false;
                }
                return true;
            });

            document.getElementById('dockMatchCount').innerText = filteredProperties.length.toLocaleString();
            document.getElementById('pillFilteredCount').innerText = filteredProperties.length.toLocaleString();

            renderMapMarkers(filteredProperties);
            renderVisiblePolygons();
            renderDockList();
            currentPage = 1;
            renderGridCards();

            if (fitStateBounds && filteredProperties.length > 0) {
                const coords = filteredProperties.filter(x => x.latitude && x.longitude).slice(0, 150).map(x => [x.latitude, x.longitude]);
                if (coords.length > 0) {
                    map.fitBounds(L.latLngBounds(coords), { padding: [50, 50], maxZoom: 11 });
                }
            }
        }

        function renderDockList() {
            const box = document.getElementById('dockList');
            const slice = filteredProperties.slice(0, 60);
            if (slice.length === 0) {
                box.innerHTML = '<div style="padding:24px; text-align:center; color:var(--text-muted); font-size:0.82rem;">No matching properties found.</div>';
                return;
            }
            box.innerHTML = slice.map(p => `
                <div class="mini-item" onclick='selectById(${p.id}, true)'>
                    <div class="mini-top">
                        <span class="mini-badge ${getBadgeClass(p.source)}">${getSourceLabel(p.source)} • ${p.state || 'US'}</span>
                        <span class="mini-price">${getDisplayPrice(p)}</span>
                    </div>
                    <div class="mini-title">${p.address || p.title || p.external_id}</div>
                    <div class="mini-sub">${p.city || ''}${p.county ? ', ' + p.county : ''} • ${p.lot_size_acres ? p.lot_size_acres + ' AC' : (p.sqft ? p.sqft.toLocaleString() + ' SF' : '')}</div>
                </div>
            `).join('');
        }

        function selectById(id, fly = true) {
            const p = ALL_PROPERTIES.find(x => x.id === id);
            if (p) selectProperty(p, fly);
        }

        // Instant Search Autocomplete
        function onSearchInput() {
            const val = document.getElementById('searchInput').value.trim();
            document.getElementById('searchClearBtn').style.display = val ? 'block' : 'none';
            const acBox = document.getElementById('autocompleteBox');

            applyFilters(false);

            if (val.length < 2) {
                acBox.style.display = 'none';
                return;
            }
            const topMatches = filteredProperties.slice(0, 8);
            if (topMatches.length === 0) {
                acBox.style.display = 'none';
                return;
            }
            acBox.innerHTML = topMatches.map(p => `
                <div class="ac-item" onclick="pickAutocomplete(${p.id})">
                    <span class="ac-title">${p.address || p.title}</span>
                    <span class="ac-sub">${getSourceLabel(p.source)} • ${p.city || ''}, ${p.state || ''} • ${p.external_id}</span>
                </div>
            `).join('');
            acBox.style.display = 'block';
        }

        function pickAutocomplete(id) {
            document.getElementById('autocompleteBox').style.display = 'none';
            selectById(id, true);
        }

        function clearSearch() {
            document.getElementById('searchInput').value = '';
            document.getElementById('searchClearBtn').style.display = 'none';
            document.getElementById('autocompleteBox').style.display = 'none';
            applyFilters(false);
        }

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrap')) {
                document.getElementById('autocompleteBox').style.display = 'none';
            }
        });

        // --- SPATIAL TOOLS (MEASURE, RESET, ZOOM) ---
        let measureMode = false;
        let measurePoints = [];
        const measureLayer = L.layerGroup().addTo(map);

        function toggleMeasureMode() {
            measureMode = !measureMode;
            document.getElementById('measureBtn').classList.toggle('active', measureMode);
            document.getElementById('measureBanner').style.display = measureMode ? 'flex' : 'none';
            document.getElementById('map').style.cursor = measureMode ? 'crosshair' : '';
            if (!measureMode) clearMeasure();
        }

        function clearMeasure() {
            measurePoints = [];
            measureLayer.clearLayers();
            document.getElementById('measureText').innerText = '📏 Click points on the satellite map to measure distance & area';
        }

        map.on('click', (e) => {
            if (!measureMode) return;
            measurePoints.push(e.latlng);
            measureLayer.clearLayers();

            measurePoints.forEach(pt => {
                L.circleMarker(pt, { radius: 5, color: '#ff2a7a', fillColor: '#fff', fillOpacity: 1, weight: 2 }).addTo(measureLayer);
            });

            if (measurePoints.length >= 2) {
                L.polyline(measurePoints, { color: '#ff2a7a', weight: 3, dashArray: '6, 6' }).addTo(measureLayer);
                let meters = 0;
                for (let i = 1; i < measurePoints.length; i++) {
                    meters += measurePoints[i-1].distanceTo(measurePoints[i]);
                }
                const feet = (meters * 3.28084).toFixed(0);
                const miles = (meters / 1609.34).toFixed(2);
                let txt = `📏 Distance: ${Number(feet).toLocaleString()} ft (${miles} mi)`;

                if (measurePoints.length >= 3) {
                    L.polygon(measurePoints, { color: '#ff2a7a', fillColor: '#ff2a7a', fillOpacity: 0.2, weight: 2 }).addTo(measureLayer);
                    const areaSqM = calcPolygonAreaSqMeters(measurePoints);
                    const acres = (areaSqM / 4046.8564224).toFixed(2);
                    txt += ` | Area: ${acres} Acres`;
                }
                document.getElementById('measureText').innerText = txt;
            }
        });

        function calcPolygonAreaSqMeters(latlngs) {
            const R = 6378137;
            let area = 0;
            for (let i = 0; i < latlngs.length; i++) {
                const p1 = latlngs[i];
                const p2 = latlngs[(i + 1) % latlngs.length];
                area += ((p2.lng - p1.lng) * Math.PI / 180) * (2 + Math.sin(p1.lat * Math.PI / 180) + Math.sin(p2.lat * Math.PI / 180));
            }
            return Math.abs(area * R * R / 2.0);
        }

        function resetUSAView() {
            closeInspector();
            map.flyTo([38.5, -96.5], 4, { duration: 0.9 });
        }

        function zoomToPolygonsDemo() {
            const parcel = filteredProperties.find(p => p.raw_data && p.raw_data.geojson_geometry) || filteredProperties[0];
            if (parcel) selectProperty(parcel, true);
        }

        function toggleDock(hide) {
            document.getElementById('leftDock').classList.toggle('collapsed', hide);
            document.getElementById('dockOpenBtn').style.display = hide ? 'block' : 'none';
        }

        // Export Filtered GeoJSON Download
        function exportFilteredGeoJSON() {
            const fc = {
                type: "FeatureCollection",
                features: filteredProperties.filter(p => p.latitude && p.longitude).map(p => ({
                    type: "Feature",
                    id: p.id,
                    geometry: (p.raw_data && p.raw_data.geojson_geometry) || { type: "Point", coordinates: [p.longitude, p.latitude] },
                    properties: {
                        id: p.id, source: p.source, external_id: p.external_id,
                        address: p.address, city: p.city, county: p.county, state: p.state,
                        price: p.price, tax_assessed_value: p.tax_assessed_value,
                        lot_size_acres: p.lot_size_acres, owner_name: p.owner_name, zoning: p.zoning
                    }
                }))
            };
            const blob = new Blob([JSON.stringify(fc)], { type: 'application/geo+json' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `geoestate_${activeSource}_${document.getElementById('stateFilter').value}.geojson`;
            a.click();
        }

        // --- VIEW 2: ANALYTICS & PAGINATED GRID ---
        function switchView(mode) {
            const isMap = mode === 'map';
            document.getElementById('mapView').style.display = isMap ? 'block' : 'none';
            document.getElementById('gridView').style.display = isMap ? 'none' : 'block';
            document.getElementById('btnMapView').classList.toggle('active', isMap);
            document.getElementById('btnGridView').classList.toggle('active', !isMap);
            if (isMap) setTimeout(() => map.invalidateSize(), 100);
            else renderGridCards();
        }

        function renderAnalyticsBars() {
            const total = ALL_PROPERTIES.length || 1;
            const sources = [
                { name: 'Zillow', count: __ZILLOW_COUNT__, color: '#38bdf8' },
                { name: 'Regrid.com', count: __REGRID_COUNT__, color: '#c084fc' },
                { name: 'LandGlide', count: __LAND_COUNT__, color: '#34d399' },
                { name: 'LoopNet', count: __LOOPNET_COUNT__, color: '#fbbf24' }
            ];
            document.getElementById('sourceBars').innerHTML = sources.map(s => `
                <div class="bar-row">
                    <span class="bar-lbl">${s.name}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:${(s.count/total*100).toFixed(1)}%; background:${s.color};"></div></div>
                    <span class="bar-num">${s.count.toLocaleString()}</span>
                </div>
            `).join('');

            const maxSt = TOP_STATES.length ? TOP_STATES[0].count : 1;
            document.getElementById('stateBars').innerHTML = TOP_STATES.slice(0, 5).map(st => `
                <div class="bar-row">
                    <span class="bar-lbl">${st.state}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:${(st.count/maxSt*100).toFixed(1)}%; background:linear-gradient(90deg,#38bdf8,#c084fc);"></div></div>
                    <span class="bar-num">${st.count.toLocaleString()}</span>
                </div>
            `).join('');
        }

        function renderGridCards() {
            const totalPages = Math.max(1, Math.ceil(filteredProperties.length / PAGE_SIZE));
            if (currentPage > totalPages) currentPage = totalPages;
            const start = (currentPage - 1) * PAGE_SIZE;
            const pageItems = filteredProperties.slice(start, start + PAGE_SIZE);

            document.getElementById('gridShowingCount').innerText = filteredProperties.length.toLocaleString();
            document.getElementById('pageIndicator').innerText = `Page ${currentPage} of ${totalPages}`;
            document.getElementById('prevPageBtn').disabled = currentPage <= 1;
            document.getElementById('nextPageBtn').disabled = currentPage >= totalPages;

            const grid = document.getElementById('cardsGrid');
            if (pageItems.length === 0) {
                grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:50px; color:var(--text-muted);">No matching properties.</div>';
                return;
            }
            grid.innerHTML = pageItems.map(p => `
                <div class="prop-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="mini-badge ${getBadgeClass(p.source)}">${getSourceLabel(p.source)}</span>
                        <span class="mini-badge" style="background:rgba(255,255,255,0.07); color:#fff;">${p.state || 'US'}</span>
                    </div>
                    <div style="font-size:1.3rem; font-weight:800; color:var(--accent-emerald);">${getDisplayPrice(p)}</div>
                    <div style="font-size:0.95rem; font-weight:700; color:#fff;">${p.address || p.title || p.external_id}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">📍 ${p.city || ''}${p.county ? ', ' + p.county : ''}, ${p.state || ''}</div>
                    <div style="font-size:0.76rem; color:var(--text-muted); background:#070b14; padding:8px 10px; border-radius:8px; border:1px solid var(--border);">
                        ${p.lot_size_acres ? `<strong>${p.lot_size_acres}</strong> AC` : ''}
                        ${p.sqft ? ` • <strong>${p.sqft.toLocaleString()}</strong> SqFt` : ''}
                        ${p.parcel_id ? ` • APN: <strong>${p.parcel_id}</strong>` : ''}
                    </div>
                    <div class="card-actions">
                        <button class="card-btn" onclick="locateOnMap(${p.id})">🛰️ Locate on Map</button>
                        <button class="card-btn" onclick="locateAndInspect(${p.id})">🔍 Details</button>
                    </div>
                </div>
            `).join('');
        }

        function changePage(delta) {
            currentPage += delta;
            renderGridCards();
            document.getElementById('gridView').scrollTo({ top: 0, behavior: 'smooth' });
        }

        function locateOnMap(id) {
            switchView('map');
            setTimeout(() => selectById(id, true), 150);
        }

        function locateAndInspect(id) {
            switchView('map');
            setTimeout(() => selectById(id, true), 150);
        }

        // Initial Render
        renderAnalyticsBars();
        applyFilters(false);
    </script>
</body>
</html>
"""

    html_output = (
        html_template
        .replace("__TOTAL_COUNT__", f"{total_count:,}")
        .replace("__ZILLOW_COUNT__", f"{zillow_count:,}")
        .replace("__LOOPNET_COUNT__", f"{loopnet_count:,}")
        .replace("__LAND_COUNT__", f"{landglide_count:,}")
        .replace("__REGRID_COUNT__", f"{regrid_count:,}")
        .replace("__COMPACT_JSON__", compact_json)
        .replace("__TOP_STATES_JSON__", top_states_json)
    )

    out_file = Path(__file__).resolve().parent / "outputs" / "dashboard.html"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(html_output, encoding="utf-8")
    print(f"Successfully generated GeoEstate Spatial UI Dashboard with {total_count} live PG properties at {out_file} ({len(html_output)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    generate_web_dashboard()
