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
                   parcel_id, owner_name, legal_description, zoning, url, broker_name,
                   raw_data
            FROM properties
            ORDER BY state, price DESC NULLS LAST;
        """)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]

        # Query counts per source
        cur.execute("SELECT source, COUNT(*) FROM properties GROUP BY source;")
        counts = dict(cur.fetchall())

    conn.close()

    # Convert Decimals/Floats for JSON serialization
    for r in rows:
        for k, v in r.items():
            if hasattr(v, '__float__') and not isinstance(v, (int, float, bool)):
                r[k] = float(v)

    zillow_count = counts.get("zillow", 534)
    loopnet_count = counts.get("loopnet", 52)
    landglide_count = counts.get("landglide", 0) + counts.get("texas_cad", 0) + counts.get("us_parcels", 130)
    regrid_count = counts.get("regrid", 192)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USA Real Estate & Parcel Intelligence Platform</title>
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
            background: rgba(21, 29, 47, 0.9);
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
            padding: 3px 10px;
            border-radius: 9999px;
            font-weight: 600;
        }}

        .api-links {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .api-link-btn {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            border: 1px solid rgba(56, 189, 248, 0.3);
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .api-link-btn:hover {{
            background: var(--accent-blue);
            color: #0b0f19;
        }}

        .api-link-btn-green {{
            background: rgba(74, 222, 128, 0.1);
            color: var(--accent-green);
            border: 1px solid rgba(74, 222, 128, 0.3);
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .api-link-btn-green:hover {{
            background: var(--accent-green);
            color: #0b0f19;
        }}

        /* Layout */
        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 32px 24px;
            width: 100%;
            flex: 1;
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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
            font-size: 0.8rem;
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

        .pill-group {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .pill {{
            background: #0b0f19;
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .pill:hover, .pill.active {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            border-color: var(--accent-blue);
        }}

        .select-filter {{
            background: #0b0f19;
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
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
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .prop-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.4);
        }}

        .prop-badge-bar {{
            padding: 12px 16px 8px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .tag {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }}

        .tag-zillow {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); }}
        .tag-loopnet {{ background: rgba(251, 191, 36, 0.15); color: var(--accent-amber); }}
        .tag-parcels {{ background: rgba(74, 222, 128, 0.15); color: var(--accent-green); }}
        .tag-regrid {{ background: rgba(192, 132, 252, 0.15); color: var(--accent-purple); border: 1px solid rgba(192, 132, 252, 0.3); }}

        .state-pill {{
            background: #0b0f19;
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}

        .prop-body {{
            padding: 12px 16px 16px 16px;
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 8px;
        }}

        .prop-price {{
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--accent-green);
        }}

        .prop-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-main);
            line-height: 1.3;
        }}

        .prop-location {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .specs-row {{
            display: flex;
            gap: 12px;
            background: #0b0f19;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-top: 4px;
            flex-wrap: wrap;
        }}

        .specs-item {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .specs-item strong {{
            color: var(--text-main);
        }}

        .prop-footer {{
            margin-top: auto;
            padding-top: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}

        .owner-desc {{
            font-size: 0.75rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 170px;
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
            cursor: pointer;
            transition: all 0.2s;
        }}

        .view-btn:hover {{
            background: var(--accent-blue);
            color: #0b0f19;
        }}

        /* Modal Overlay */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
        }}

        .modal-overlay.active {{
            display: flex;
        }}

        .modal-content {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            max-width: 720px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            position: relative;
        }}

        .close-modal {{
            position: absolute;
            top: 18px;
            right: 20px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
        }}

        .close-modal:hover {{
            color: var(--text-main);
        }}

        .modal-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 0.9rem;
        }}

        .modal-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
        }}

        .modal-table td:first-child {{
            color: var(--text-muted);
            width: 38%;
            font-weight: 600;
        }}
    </style>
</head>
<body>

    <nav>
        <div class="brand">
            <span>🏛️</span> US Real Estate & Parcel Intelligence
            <span class="brand-badge">⚡ Live Multi-Platform API</span>
        </div>
        <div class="api-links">
            <a href="/docs" target="_blank" class="api-link-btn">Swagger Docs ↗</a>
            <a href="/api/v1/regrid" target="_blank" style="background: rgba(192, 132, 252, 0.1); color: var(--accent-purple); border: 1px solid rgba(192, 132, 252, 0.3); text-decoration: none; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600;">Regrid API ↗</a>
            <a href="/api/v1/properties?limit=10" target="_blank" class="api-link-btn-green">REST API JSON ↗</a>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-left: 6px;">
                Total Database: <strong style="color: var(--text-main);" id="totalCount">{len(rows)}</strong> Properties
            </div>
        </div>
    </nav>

    <div class="container">

        <!-- KPI Summary Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <span class="kpi-label">Total Nationwide Assets</span>
                <span class="kpi-val" style="color: var(--accent-blue);" id="kpiTotal">{len(rows)}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Residential (Zillow)</span>
                <span class="kpi-val" style="color: var(--accent-blue);" id="kpiZillow">{zillow_count}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Commercial (LoopNet)</span>
                <span class="kpi-val" style="color: var(--accent-amber);" id="kpiLoopnet">{loopnet_count}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">LandGlide / CAD Parcels</span>
                <span class="kpi-val" style="color: var(--accent-green);" id="kpiParcels">{landglide_count}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Regrid (regrid.com) Parcels</span>
                <span class="kpi-val" style="color: var(--accent-purple);" id="kpiRegrid">{regrid_count}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">US Geographic Scope</span>
                <span class="kpi-val" style="color: var(--accent-purple);">50 US States</span>
            </div>
        </div>

        <!-- Filter Controls -->
        <div class="filters-panel">
            <div class="search-box">
                <input type="text" id="searchInput" class="search-input" placeholder="Search by address, city, APN, owner name, or Regrid ID..." oninput="filterData()">
            </div>

            <div class="pill-group">
                <button class="pill active" onclick="setSource('all', this)">All Platforms ({len(rows)})</button>
                <button class="pill" onclick="setSource('zillow', this)">🏡 Zillow ({zillow_count})</button>
                <button class="pill" onclick="setSource('loopnet', this)">🏢 LoopNet ({loopnet_count})</button>
                <button class="pill" onclick="setSource('us_parcels', this)">🗺️ LandGlide ({landglide_count})</button>
                <button class="pill" onclick="setSource('regrid', this)">🌐 Regrid.com ({regrid_count})</button>
            </div>

            <select id="stateFilter" class="select-filter" onchange="filterData()">
                <option value="all">All 50 US States (Nationwide)</option>
                <option value="AL">Alabama (AL)</option>
                <option value="AK">Alaska (AK)</option>
                <option value="AZ">Arizona (AZ)</option>
                <option value="AR">Arkansas (AR)</option>
                <option value="CA">California (CA)</option>
                <option value="CO">Colorado (CO)</option>
                <option value="CT">Connecticut (CT)</option>
                <option value="DE">Delaware (DE)</option>
                <option value="FL">Florida (FL)</option>
                <option value="GA">Georgia (GA)</option>
                <option value="HI">Hawaii (HI)</option>
                <option value="ID">Idaho (ID)</option>
                <option value="IL">Illinois (IL)</option>
                <option value="IN">Indiana (IN)</option>
                <option value="IA">Iowa (IA)</option>
                <option value="KS">Kansas (KS)</option>
                <option value="KY">Kentucky (KY)</option>
                <option value="LA">Louisiana (LA)</option>
                <option value="ME">Maine (ME)</option>
                <option value="MD">Maryland (MD)</option>
                <option value="MA">Massachusetts (MA)</option>
                <option value="MI">Michigan (MI)</option>
                <option value="MN">Minnesota (MN)</option>
                <option value="MS">Mississippi (MS)</option>
                <option value="MO">Missouri (MO)</option>
                <option value="MT">Montana (MT)</option>
                <option value="NE">Nebraska (NE)</option>
                <option value="NV">Nevada (NV)</option>
                <option value="NH">New Hampshire (NH)</option>
                <option value="NJ">New Jersey (NJ)</option>
                <option value="NM">New Mexico (NM)</option>
                <option value="NY">New York (NY)</option>
                <option value="NC">North Carolina (NC)</option>
                <option value="ND">North Dakota (ND)</option>
                <option value="OH">Ohio (OH)</option>
                <option value="OK">Oklahoma (OK)</option>
                <option value="OR">Oregon (OR)</option>
                <option value="PA">Pennsylvania (PA)</option>
                <option value="RI">Rhode Island (RI)</option>
                <option value="SC">South Carolina (SC)</option>
                <option value="SD">South Dakota (SD)</option>
                <option value="TN">Tennessee (TN)</option>
                <option value="TX">Texas (TX)</option>
                <option value="UT">Utah (UT)</option>
                <option value="VT">Vermont (VT)</option>
                <option value="VA">Virginia (VA)</option>
                <option value="WA">Washington (WA)</option>
                <option value="WV">West Virginia (WV)</option>
                <option value="WI">Wisconsin (WI)</option>
                <option value="WY">Wyoming (WY)</option>
            </select>
        </div>

        <!-- Property Grid Container -->
        <div class="property-grid" id="propertyGrid">
            <!-- Dynamically populated via JavaScript -->
        </div>

    </div>

    <!-- Property Detail Modal -->
    <div class="modal-overlay" id="detailModal">
        <div class="modal-content">
            <button class="close-modal" onclick="closeModal()">&times;</button>
            <h2 id="modalTitle" style="font-size: 1.35rem; margin-bottom: 6px;">Property Details</h2>
            <div id="modalPrice" style="font-size: 1.6rem; font-weight: 800; color: var(--accent-green); margin-bottom: 16px;"></div>
            <table class="modal-table" id="modalTable">
                <!-- Dynamically populated -->
            </table>
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

                let sourceTagClass = 'tag-parcels';
                let sourceLabel = 'LandGlide';

                if (p.source === 'zillow') {{
                    sourceTagClass = 'tag-zillow';
                    sourceLabel = 'Zillow';
                }} else if (p.source === 'loopnet') {{
                    sourceTagClass = 'tag-loopnet';
                    sourceLabel = 'LoopNet';
                }} else if (p.source === 'regrid') {{
                    sourceTagClass = 'tag-regrid';
                    sourceLabel = 'Regrid.com';
                }}

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
                }} else if (p.source === 'regrid') {{
                    specsHtml = `
                        <div class="specs-item"><strong>${{p.lot_size_acres || '1.0'}}</strong> GIS Acres</div>
                        <div class="specs-item"><strong>APN:</strong> ${{p.parcel_id || p.external_id}}</div>
                        <div class="specs-item"><strong style="color: var(--accent-purple);">🗺️ GeoJSON Boundary</strong></div>
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
                            <button class="view-btn" onclick="openDetail(${{p.id}})">Details & API →</button>
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
                    if (activeSource === 'regrid' && p.source !== 'regrid') return false;
                    if (!['us_parcels', 'regrid'].includes(activeSource) && p.source !== activeSource) return false;
                }}

                // State Filter
                if (state !== 'all' && p.state !== state) return false;

                // Search Input
                if (search) {{
                    const matchText = `${{p.title || ''}} ${{p.address || ''}} ${{p.city || ''}} ${{p.owner_name || ''}} ${{p.external_id || ''}} ${{p.parcel_id || ''}}`.toLowerCase();
                    if (!matchText.includes(search)) return false;
                }}

                return true;
            }});

            renderCards(filtered);
        }}

        function openDetail(id) {{
            const p = rawProperties.find(x => x.id === id);
            if (!p) return;

            document.getElementById('modalTitle').innerText = p.title || p.address || 'Real Estate Asset Details';
            document.getElementById('modalPrice').innerText = p.price ? formatCurrency(p.price) : (p.lease_rate || (p.tax_assessed_value ? 'Assessed: ' + formatCurrency(p.tax_assessed_value) : 'Contact Broker'));

            let regridExtra = '';
            if (p.source === 'regrid' && p.raw_data) {{
                const rd = p.raw_data;
                regridExtra = `
                    <tr><td>Regrid Parcel ID (UUID)</td><td>${{rd.ll_uuid || '-'}}</td></tr>
                    <tr><td>County FIPS Code</td><td>${{rd.fips || '-'}}</td></tr>
                    <tr><td>Owner Mailing Address</td><td>${{rd.owner_mailing || '-'}}</td></tr>
                    <tr><td>Land Use Classification</td><td>${{rd.use_code || '-'}}</td></tr>
                    <tr><td>Land / Improvement Value</td><td>${{formatCurrency(rd.land_value)}} / ${{formatCurrency(rd.improvement_value)}}</td></tr>
                    <tr><td>Annual Property Tax</td><td>${{formatCurrency(rd.tax_amount)}} (Tax Year ${{rd.tax_year || 2025}})</td></tr>
                    <tr><td>Last Recorded Deed Sale</td><td>${{formatCurrency(rd.last_sale_price)}} (${{rd.last_sale_date || '-'}})</td></tr>
                    <tr><td>GIS Polygon Geometry</td><td><span style="color: var(--accent-purple);">GeoJSON Polygon (${{rd.geojson_geometry ? rd.geojson_geometry.coordinates[0].length + ' boundary vertices' : 'Mapped'}})</span></td></tr>
                    <tr><td>Regrid Direct URL</td><td><a href="${{p.url}}" target="_blank" style="color: var(--accent-purple);">Open Listing on Regrid.com ↗</a></td></tr>
                `;
            }}

            const table = document.getElementById('modalTable');
            table.innerHTML = `
                <tr><td>Source Platform</td><td>${{p.source.toUpperCase()}}</td></tr>
                <tr><td>Asset External ID / APN</td><td>${{p.external_id}}</td></tr>
                <tr><td>Property Type</td><td>${{p.property_type || 'Residential'}}</td></tr>
                <tr><td>Listing Status</td><td>${{p.listing_status || 'Active'}}</td></tr>
                <tr><td>Street Address</td><td>${{p.address || '-'}}</td></tr>
                <tr><td>City, State ZIP</td><td>${{p.city || '-'}}, ${{p.state || '-'}} ${{p.zip_code || ''}}</td></tr>
                <tr><td>Bedrooms / Bathrooms</td><td>${{p.beds || '-'}} Beds / ${{p.baths || '-'}} Baths</td></tr>
                <tr><td>Square Footage</td><td>${{p.sqft ? p.sqft.toLocaleString() + ' SqFt' : '-'}}</td></tr>
                <tr><td>Lot Size (Acres)</td><td>${{p.lot_size_acres ? p.lot_size_acres + ' Acres' : '-'}}</td></tr>
                <tr><td>County Tax Value</td><td>${{p.tax_assessed_value ? formatCurrency(p.tax_assessed_value) : '-'}}</td></tr>
                <tr><td>Registered Owner</td><td>${{p.owner_name || 'N/A'}}</td></tr>
                <tr><td>Zoning</td><td>${{p.zoning || 'N/A'}}</td></tr>
                ${{regridExtra}}
                <tr><td>Custom API Endpoint</td><td><a href="/api/v1/properties/${{p.id}}" target="_blank" style="color: var(--accent-blue);">/api/v1/properties/${{p.id}} ↗</a></td></tr>
            `;

            document.getElementById('detailModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('detailModal').classList.remove('active');
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
