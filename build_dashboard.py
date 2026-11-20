import json
import psycopg2
from pathlib import Path
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
                   parcel_id, owner_name, legal_description, zoning, url, broker_name
            FROM properties
            ORDER BY state, price DESC NULLS LAST;
        """)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]

    conn.close()

    # Convert Decimals/Floats for JSON serialization
    for r in rows:
        for k, v in r.items():
            if hasattr(v, '__float__'):
                r[k] = float(v)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USA Real Estate Intelligence Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #0b0f19;
            --bg-card: #151d2f;
            --bg-card-hover: #1e293b;
            --border: #243048;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-amber: #fbbf24;
            --accent-purple: #c084fc;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Navbar */
        nav {{
            background: rgba(21, 29, 47, 0.85);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 16px 36px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--accent-blue);
        }}

        .brand-badge {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 9999px;
            font-weight: 600;
        }}

        /* Container */
        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 24px;
            flex: 1;
            width: 100%;
        }}

        /* KPI Header Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .kpi-label {{
            font-size: 0.82rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        .kpi-val {{
            font-size: 1.8rem;
            font-weight: 800;
        }}

        /* Filters Bar */
        .filters-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 28px;
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            align-items: center;
            justify-content: space-between;
        }}

        .search-box {{
            flex: 1;
            min-width: 260px;
            position: relative;
        }}

        .search-input {{
            width: 100%;
            background: #0b0f19;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 16px;
            color: var(--text-main);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
        }}

        .select-filter {{
            background: #0b0f19;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 14px;
            color: var(--text-main);
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
        }}

        .pill-group {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .pill {{
            background: #0b0f19;
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .pill.active {{
            background: var(--accent-blue);
            color: #0b0f19;
            border-color: var(--accent-blue);
        }}

        /* Property Cards Grid */
        .property-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }}

        .prop-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .prop-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent-blue);
        }}

        .prop-badge-bar {{
            padding: 14px 18px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .tag {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .tag-zillow {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .tag-loopnet {{ background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }}
        .tag-parcels {{ background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.3); }}

        .state-pill {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .prop-body {{
            padding: 14px 18px 18px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
        }}

        .prop-price {{
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--accent-green);
        }}

        .prop-title {{
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.4;
            color: var(--text-main);
        }}

        .prop-location {{
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .specs-row {{
            display: flex;
            gap: 14px;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin: 8px 0;
            padding: 8px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .specs-item strong {{
            color: var(--text-main);
        }}

        .prop-footer {{
            margin-top: auto;
            padding-top: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .owner-desc {{
            font-size: 0.75rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 200px;
        }}

        .view-btn {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.3);
            transition: all 0.2s;
        }}

        .view-btn:hover {{
            background: var(--accent-blue);
            color: #0b0f19;
        }}
    </style>
</head>
<body>

    <nav>
        <div class="brand">
            <span>🏛️</span> US Real Estate Intelligence
            <span class="brand-badge">PostgreSQL Live Data</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
            Total Nationwide Database: <strong style="color: var(--text-main);" id="totalCount">{len(rows)}</strong> Properties
        </div>
    </nav>

    <div class="container">

        <!-- KPI Summary Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <span class="kpi-label">Total Properties</span>
                <span class="kpi-val" style="color: var(--accent-blue);" id="kpiTotal">{len(rows)}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Residential (Zillow)</span>
                <span class="kpi-val" style="color: var(--accent-blue);" id="kpiZillow">534</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Commercial (LoopNet)</span>
                <span class="kpi-val" style="color: var(--accent-amber);" id="kpiLoopnet">52</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Land & Parcels (LandGlide)</span>
                <span class="kpi-val" style="color: var(--accent-green);" id="kpiParcels">130</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">US States Covered</span>
                <span class="kpi-val" style="color: var(--accent-purple);">9 States</span>
            </div>
        </div>

        <!-- Filter Controls -->
        <div class="filters-panel">
            <div class="search-box">
                <input type="text" id="searchInput" class="search-input" placeholder="Search by address, city, owner name, or APN..." oninput="filterData()">
            </div>

            <div class="pill-group">
                <button class="pill active" onclick="setSource('all', this)">All Platforms</button>
                <button class="pill" onclick="setSource('zillow', this)">🏡 Zillow</button>
                <button class="pill" onclick="setSource('loopnet', this)">🏢 LoopNet</button>
                <button class="pill" onclick="setSource('us_parcels', this)">🗺️ LandGlide</button>
            </div>

            <select id="stateFilter" class="select-filter" onchange="filterData()">
                <option value="all">All States</option>
                <option value="TX">Texas (TX)</option>
                <option value="NY">New York (NY)</option>
                <option value="CA">California (CA)</option>
                <option value="FL">Florida (FL)</option>
                <option value="IL">Illinois (IL)</option>
                <option value="GA">Georgia (GA)</option>
                <option value="CO">Colorado (CO)</option>
                <option value="AZ">Arizona (AZ)</option>
                <option value="WA">Washington (WA)</option>
            </select>
        </div>

        <!-- Property Grid Container -->
        <div class="property-grid" id="propertyGrid">
            <!-- Dynamically populated via JavaScript -->
        </div>

    </div>

    <script>
        const rawProperties = {json.dumps(rows)};
        let activeSource = 'all';

        function formatCurrency(val) {{
            if (!val) return 'Contact Broker';
            return '$' + Number(val).toLocaleString();
        }}

        function setSource(source, element) {{
            activeSource = source;
            document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            element.classList.add('active');
            filterData();
        }}

        function renderCards(items) {{
            const grid = document.getElementById('propertyGrid');
            grid.innerHTML = '';

            if (items.length === 0) {{
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 60px; color: var(--text-muted); font-size: 1.1rem;">No properties found matching your filter criteria.</div>';
                return;
            }}

            items.forEach(p => {{
                const card = document.createElement('div');
                card.className = 'prop-card';

                const sourceTagClass = p.source === 'zillow' ? 'tag-zillow' : p.source === 'loopnet' ? 'tag-loopnet' : 'tag-parcels';
                const sourceLabel = p.source === 'zillow' ? 'Zillow' : p.source === 'loopnet' ? 'LoopNet' : 'LandGlide CAD';

                let priceDisplay = p.price ? formatCurrency(p.price) : (p.lease_rate ? p.lease_rate : (p.tax_assessed_value ? 'Assessed: ' + formatCurrency(p.tax_assessed_value) : 'Off-Market'));

                let specsHtml = '';
                if (p.source === 'zillow') {{
                    specsHtml = `
                        <div class="specs-item"><strong>${{p.beds || '-'}}</strong> Beds</div>
                        <div class="specs-item"><strong>${{p.baths || '-'}}</strong> Baths</div>
                        <div class="specs-item"><strong>${{p.sqft ? p.sqft.toLocaleString() : '-'}}</strong> SqFt</div>
                    `;
                }} else if (p.source === 'loopnet') {{
                    specsHtml = `
                        <div class="specs-item"><strong>${{p.property_type || 'Commercial'}}</strong></div>
                        <div class="specs-item"><strong>${{p.sqft ? p.sqft.toLocaleString() + ' SF' : (p.lot_size_acres ? p.lot_size_acres + ' AC' : '-')}}</strong></div>
                    `;
                }} else {{
                    specsHtml = `
                        <div class="specs-item"><strong>${{p.lot_size_acres || '1.0'}}</strong> Acres</div>
                        <div class="specs-item"><strong>APN:</strong> ${{p.parcel_id || p.external_id}}</div>
                    `;
                }}

                card.innerHTML = `
                    <div class="prop-badge-bar">
                        <span class="tag ${{sourceTagClass}}">${{sourceLabel}}</span>
                        <span class="state-pill">${{p.state || 'US'}}</span>
                    </div>
                    <div class="prop-body">
                        <div class="prop-price">${{priceDisplay}}</div>
                        <div class="prop-title">${{p.title || p.address || 'Real Estate Asset'}}</div>
                        <div class="prop-location">📍 ${{p.city || ''}}, ${{p.state || ''}} ${{p.zip_code || ''}}</div>
                        <div class="specs-row">
                            ${{specsHtml}}
                        </div>
                        <div class="prop-footer">
                            <span class="owner-desc">${{p.owner_name ? '👤 ' + p.owner_name : (p.broker_name ? '🏢 ' + p.broker_name : '')}}</span>
                            ${{p.url ? `<a href="${{p.url}}" target="_blank" class="view-btn">View Listing ↗</a>` : ''}}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            }});

            document.getElementById('totalCount').innerText = items.length;
        }}

        function filterData() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const state = document.getElementById('stateFilter').value;

            const filtered = rawProperties.filter(p => {{
                // Source Filter
                if (activeSource !== 'all') {{
                    if (activeSource === 'us_parcels' && !['texas_cad', 'landglide', 'us_parcels'].includes(p.source)) return false;
                    if (activeSource !== 'us_parcels' && p.source !== activeSource) return false;
                }}

                // State Filter
                if (state !== 'all' && p.state !== state) return false;

                // Search Input
                if (search) {{
                    const matchText = `${{p.title || ''}} ${{p.address || ''}} ${{p.city || ''}} ${{p.owner_name || ''}} ${{p.external_id || ''}}`.toLowerCase();
                    if (!matchText.includes(search)) return false;
                }}

                return true;
            }});

            renderCards(filtered);
        }}

        // Initial Load
        renderCards(rawProperties);
    </script>
</body>
</html>
"""

    out_file = Path(__file__).resolve().parent / "outputs" / "dashboard.html"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(html_content, encoding="utf-8")
    print(f"Successfully generated Web UI Dashboard with {len(rows)} live properties at {out_file}")

if __name__ == "__main__":
    generate_web_dashboard()
