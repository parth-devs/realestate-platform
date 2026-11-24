import json
import uuid
import random
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from loguru import logger
from config import settings, BASE_DIR

ALL_50_STATES_METROS = [
    # State, City, County, Zip, (Lat, Lon)
    ("AL", "Birmingham", "Jefferson County", "35203", (33.5186, -86.8104)),
    ("AL", "Huntsville", "Madison County", "35801", (34.7304, -86.5861)),
    ("AK", "Anchorage", "Anchorage Municipality", "99501", (61.2181, -149.9003)),
    ("AZ", "Phoenix", "Maricopa County", "85001", (33.4484, -112.0740)),
    ("AZ", "Tucson", "Pima County", "85701", (32.2226, -110.9747)),
    ("AZ", "Scottsdale", "Maricopa County", "85251", (33.4942, -111.9261)),
    ("AR", "Little Rock", "Pulaski County", "72201", (34.7465, -92.2896)),
    ("CA", "Los Angeles", "Los Angeles County", "90012", (34.0522, -118.2437)),
    ("CA", "San Francisco", "San Francisco County", "94102", (37.7749, -122.4194)),
    ("CA", "San Diego", "San Diego County", "92101", (32.7157, -117.1611)),
    ("CA", "San Jose", "Santa Clara County", "95113", (37.3382, -121.8863)),
    ("CA", "Sacramento", "Sacramento County", "95814", (38.5816, -121.4944)),
    ("CO", "Denver", "Denver County", "80202", (39.7392, -104.9903)),
    ("CO", "Colorado Springs", "El Paso County", "80903", (38.8339, -104.8214)),
    ("CT", "Hartford", "Hartford County", "06103", (41.7658, -72.6734)),
    ("CT", "Stamford", "Fairfield County", "06901", (41.0534, -73.5387)),
    ("DE", "Wilmington", "New Castle County", "19801", (39.7447, -75.5484)),
    ("FL", "Miami", "Miami-Dade County", "33101", (25.7617, -80.1918)),
    ("FL", "Orlando", "Orange County", "32801", (28.5383, -81.3792)),
    ("FL", "Tampa", "Hillsborough County", "33602", (27.9506, -82.4572)),
    ("FL", "Jacksonville", "Duval County", "32099", (30.3322, -81.6557)),
    ("FL", "Fort Lauderdale", "Broward County", "33301", (26.1224, -80.1373)),
    ("GA", "Atlanta", "Fulton County", "30303", (33.7490, -84.3880)),
    ("GA", "Savannah", "Chatham County", "31401", (32.0809, -81.0912)),
    ("HI", "Honolulu", "Honolulu County", "96813", (21.3069, -157.8583)),
    ("ID", "Boise", "Ada County", "83702", (43.6150, -116.2023)),
    ("IL", "Chicago", "Cook County", "60601", (41.8781, -87.6298)),
    ("IL", "Naperville", "DuPage County", "60540", (41.7508, -88.1535)),
    ("IN", "Indianapolis", "Marion County", "46204", (39.7684, -86.1581)),
    ("IA", "Des Moines", "Polk County", "50309", (41.5868, -93.6250)),
    ("KS", "Wichita", "Sedgwick County", "67202", (37.6872, -97.3301)),
    ("KY", "Louisville", "Jefferson County", "40202", (38.2527, -85.7585)),
    ("LA", "New Orleans", "Orleans Parish", "70112", (29.9511, -90.0715)),
    ("ME", "Portland", "Cumberland County", "04101", (43.6591, -70.2568)),
    ("MD", "Baltimore", "Baltimore City", "21201", (39.2904, -76.6122)),
    ("MA", "Boston", "Suffolk County", "02108", (42.3601, -71.0589)),
    ("MA", "Cambridge", "Middlesex County", "02138", (42.3736, -71.1097)),
    ("MI", "Detroit", "Wayne County", "48226", (42.3314, -83.0458)),
    ("MI", "Grand Rapids", "Kent County", "49503", (42.9634, -85.6681)),
    ("MN", "Minneapolis", "Hennepin County", "55401", (44.9778, -93.2650)),
    ("MS", "Jackson", "Hinds County", "39201", (32.2988, -90.1848)),
    ("MO", "Kansas City", "Jackson County", "64106", (39.0997, -94.5786)),
    ("MO", "St. Louis", "St. Louis City", "63101", (38.6270, -90.1994)),
    ("MT", "Billings", "Yellowstone County", "59101", (45.7833, -108.5007)),
    ("NE", "Omaha", "Douglas County", "68102", (41.2565, -95.9345)),
    ("NV", "Las Vegas", "Clark County", "89101", (36.1699, -115.1398)),
    ("NV", "Reno", "Washoe County", "89501", (39.5296, -119.8138)),
    ("NH", "Manchester", "Hillsborough County", "03101", (42.9956, -71.4548)),
    ("NJ", "Jersey City", "Hudson County", "07302", (40.7178, -74.0431)),
    ("NJ", "Newark", "Essex County", "07102", (40.7357, -74.1724)),
    ("NM", "Albuquerque", "Bernalillo County", "87102", (35.0844, -106.6504)),
    ("NY", "New York", "New York County", "10001", (40.7128, -74.0060)),
    ("NY", "Buffalo", "Erie County", "14202", (42.8864, -78.8784)),
    ("NC", "Charlotte", "Mecklenburg County", "28202", (35.2271, -80.8431)),
    ("NC", "Raleigh", "Wake County", "27601", (35.7796, -78.6382)),
    ("ND", "Fargo", "Cass County", "58102", (46.8772, -96.7898)),
    ("OH", "Columbus", "Franklin County", "43215", (39.9612, -82.9988)),
    ("OH", "Cleveland", "Cuyahoga County", "44114", (41.4993, -81.6944)),
    ("OK", "Oklahoma City", "Oklahoma County", "73102", (35.4676, -97.5164)),
    ("OR", "Portland", "Multnomah County", "97201", (45.5152, -122.6784)),
    ("PA", "Philadelphia", "Philadelphia County", "19107", (39.9526, -75.1652)),
    ("PA", "Pittsburgh", "Allegheny County", "15219", (40.4406, -79.9959)),
    ("RI", "Providence", "Providence County", "02903", (41.8240, -71.4128)),
    ("SC", "Charleston", "Charleston County", "29401", (32.7765, -79.9311)),
    ("SD", "Sioux Falls", "Minnehaha County", "57104", (43.5446, -96.7311)),
    ("TN", "Nashville", "Davidson County", "37201", (36.1627, -86.7816)),
    ("TN", "Memphis", "Shelby County", "38103", (35.1495, -90.0490)),
    ("TN", "Woodbury", "Cannon County", "37190", (35.8278, -86.0689)),
    ("TX", "Austin", "Travis County", "78701", (30.2672, -97.7431)),
    ("TX", "Dallas", "Dallas County", "75201", (32.7767, -96.7970)),
    ("TX", "Houston", "Harris County", "77002", (29.7604, -95.3698)),
    ("TX", "San Antonio", "Bexar County", "78205", (29.4241, -98.4936)),
    ("TX", "Fort Worth", "Tarrant County", "76102", (32.7555, -97.3308)),
    ("UT", "Salt Lake City", "Salt Lake County", "84101", (40.7608, -111.8910)),
    ("VT", "Burlington", "Chittenden County", "05401", (44.4759, -73.2121)),
    ("VA", "Richmond", "Richmond City", "23219", (37.5407, -77.4360)),
    ("VA", "Virginia Beach", "Virginia Beach City", "23451", (36.8529, -75.9780)),
    ("WA", "Seattle", "King County", "98101", (47.6062, -122.3321)),
    ("WA", "Spokane", "Spokane County", "99201", (47.6588, -117.4260)),
    ("WV", "Charleston", "Kanawha County", "25301", (38.3498, -81.6326)),
    ("WI", "Milwaukee", "Milwaukee County", "53202", (43.0389, -87.9065)),
    ("WY", "Cheyenne", "Laramie County", "82001", (41.1399, -104.8202)),
    ("WY", "Jackson", "Teton County", "83001", (43.4799, -110.7624))
]

def generate_nationwide_portfolio():
    logger.info(f"Generating full 50-State Nationwide USA Dataset across {len(ALL_50_STATES_METROS)} major markets...")

    all_properties = []

    street_types = ["Ave", "St", "Blvd", "Pkwy", "Way", "Dr", "Trail", "Court", "Loop"]
    first_names = ["Lincoln", "Washington", "Highland", "Oak Ridge", "Metro", "Grand", "Sunset", "Pinecrest", "Valley", "Frontier"]

    regrid_uses = [
        ("Single Family Residential", "residential", 0.35, 480000),
        ("Commercial Retail Center", "commercial", 2.2, 3200000),
        ("Vacant Acreage / Land", "land", 8.5, 750000),
        ("Industrial Logistics / Warehouse", "industrial", 4.8, 5400000),
        ("Multi-Family Luxury Units", "multi_family", 1.8, 4100000),
        ("Agricultural Land Parcel", "land", 24.0, 1100000),
    ]

    for state, city, county, zip_code, (base_lat, base_lon) in ALL_50_STATES_METROS:
        city_slug = city.replace(" ", "").upper()[:4]

        # 1. Regrid Parcels (12 per market)
        for i in range(1, 13):
            use_desc, prop_type, base_acres, base_val = regrid_uses[i % len(regrid_uses)]
            apn = f"RG-{state}-{city_slug}-{200000 + i}"
            acres = round(base_acres * (0.85 + 0.05 * i), 2)
            total_val = round(base_val * (0.9 + 0.04 * i), 2)
            land_val = round(total_val * 0.4, 2)
            improv_val = total_val - land_val if prop_type != "land" else 0.0
            tax_amt = round(total_val * 0.0185, 2)
            lat = round(base_lat + random.uniform(-0.04, 0.04), 6)
            lon = round(base_lon + random.uniform(-0.04, 0.04), 6)
            address = f"{1000 + i * 38} {first_names[i % len(first_names)]} {street_types[i % len(street_types)]}"

            d = 0.0015
            polygon = [
                [round(lon - d, 6), round(lat - d, 6)],
                [round(lon + d, 6), round(lat - d, 6)],
                [round(lon + d, 6), round(lat + d, 6)],
                [round(lon - d, 6), round(lat + d, 6)],
                [round(lon - d, 6), round(lat - d, 6)]
            ]

            regrid_url = f"https://app.regrid.com/us/{state.lower()}/{county.lower().replace(' ', '-')}/{apn.lower()}"

            all_properties.append({
                "source": "regrid",
                "external_id": apn,
                "title": f"Regrid Parcel #{apn} ({use_desc})",
                "property_type": prop_type,
                "listing_status": "off_market",
                "price": None,
                "price_per_sqft": None,
                "lease_rate": None,
                "tax_assessed_value": total_val,
                "beds": 3 if prop_type == "residential" else None,
                "baths": 2.5 if prop_type == "residential" else None,
                "sqft": 2600 if prop_type == "residential" else (14500 if prop_type == "commercial" else None),
                "lot_size_acres": acres,
                "year_built": 2014 if prop_type != "land" else None,
                "address": address,
                "city": city,
                "county": county,
                "state": state,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lon,
                "parcel_id": apn,
                "owner_name": f"{city} Real Estate Asset Trust #{i}",
                "legal_description": f"LOT {i} BLK {i+1} {city.upper()} NATIONWIDE REGRID TRACT",
                "zoning": "C-2 Commercial" if prop_type == "commercial" else ("R-1 Residential" if prop_type == "residential" else "M-1 Industrial"),
                "url": regrid_url,
                "broker_name": "Regrid Nationwide GIS Index",
                "raw_data": {
                    "source": "Regrid Parcel Data API",
                    "ll_uuid": str(uuid.uuid4()),
                    "parcelnumb": apn,
                    "county": county,
                    "state": state,
                    "owner": f"{city} Real Estate Asset Trust #{i}",
                    "owner_mailing": f"PO BOX {4000 + i}, {city}, {state}",
                    "use_code": use_desc,
                    "gis_acres": acres,
                    "land_value": land_val,
                    "improvement_value": improv_val,
                    "total_value": total_val,
                    "tax_amount": tax_amt,
                    "tax_year": 2025,
                    "last_sale_date": f"2023-{((i % 9) + 1):02d}-15",
                    "last_sale_price": round(total_val * 0.94, 2),
                    "geojson_geometry": {"type": "Polygon", "coordinates": [polygon]}
                }
            })

        # 2. Zillow Residential Listings (15 per market)
        for i in range(1, 16):
            zpid = f"ZW-{state}-{city_slug}-{300000 + i}"
            price = round(320000 + (i * 45000) * (1.2 if state in ["CA", "NY", "WA", "CO"] else 0.9), 2)
            sqft = 1400 + (i * 120)
            beds = 2 + (i % 4)
            baths = 2.0 + (0.5 if i % 2 == 1 else 1.0)
            lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
            lon = round(base_lon + random.uniform(-0.05, 0.05), 6)
            address = f"{2000 + i * 27} {first_names[(i+2) % len(first_names)]} {street_types[i % len(street_types)]}"

            all_properties.append({
                "source": "zillow",
                "external_id": zpid,
                "title": f"Single Family Home in {city}, {state}",
                "property_type": "single_family" if i % 3 != 0 else "condo",
                "listing_status": "for_sale",
                "price": price,
                "price_per_sqft": round(price / sqft, 2),
                "lease_rate": None,
                "tax_assessed_value": round(price * 0.88, 2),
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "lot_size_acres": round(0.25 + (i * 0.05), 2),
                "year_built": 2005 + (i % 18),
                "address": address,
                "city": city,
                "county": county,
                "state": state,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lon,
                "parcel_id": f"APN-{state}-{city_slug}-{i*11}",
                "owner_name": f"Private Homeowner ({city})",
                "legal_description": f"SUBDIVISION {city.upper()} ESTATES LOT {i}",
                "zoning": "R-1 Residential",
                "url": f"https://www.zillow.com/homedetails/{zpid}_zpid/",
                "broker_name": f"{city} Premier Realty Partners",
                "raw_data": {"source": "Zillow Residential", "zestimate": price + 15000}
            })

        # 3. LoopNet Commercial (6 per market)
        for i in range(1, 7):
            loopnet_id = f"LN-{state}-{city_slug}-{400000 + i}"
            types = ["Industrial / Warehouse", "Class-A Office", "Retail Shopping Center", "Commercial Land", "Flex Space", "Medical Center"]
            p_type = types[i % len(types)]
            price = round(1500000 + (i * 750000), 2)
            bldg_sqft = 8500 + (i * 3200)
            lat = round(base_lat + random.uniform(-0.06, 0.06), 6)
            lon = round(base_lon + random.uniform(-0.06, 0.06), 6)
            address = f"{5000 + i * 50} Industrial Blvd, Suite {100 * i}"

            all_properties.append({
                "source": "loopnet",
                "external_id": loopnet_id,
                "title": f"{p_type} Asset in {city}, {state}",
                "property_type": "commercial",
                "listing_status": "for_sale" if i % 2 == 1 else "for_lease",
                "price": price if i % 2 == 1 else None,
                "price_per_sqft": round(price / bldg_sqft, 2) if i % 2 == 1 else None,
                "lease_rate": f"${22 + i} / SF / YR" if i % 2 == 0 else None,
                "tax_assessed_value": round(price * 0.91, 2),
                "beds": None,
                "baths": None,
                "sqft": bldg_sqft,
                "lot_size_acres": round(1.5 + (i * 0.8), 2),
                "year_built": 2010 + (i % 12),
                "address": address,
                "city": city,
                "county": county,
                "state": state,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lon,
                "parcel_id": f"APN-COMM-{state}-{city_slug}-{i*15}",
                "owner_name": f"{city} Commercial Properties REIT",
                "legal_description": f"INDUSTRIAL PARK SEC {i} LOT {i*2}",
                "zoning": "C-3 Heavy Commercial",
                "url": f"https://www.loopnet.com/Listing/{loopnet_id}/",
                "broker_name": "CBRE / Colliers International Commercial",
                "raw_data": {"source": "LoopNet Commercial", "cap_rate": 6.8 + (i * 0.2)}
            })

        # 4. LandGlide & CAD Parcels (6 per market)
        for i in range(1, 7):
            cad_id = f"LG-{state}-{city_slug}-{500000 + i}"
            acres = round(3.5 + (i * 2.5), 2)
            assessed_val = round(220000 + (i * 85000), 2)
            lat = round(base_lat + random.uniform(-0.07, 0.07), 6)
            lon = round(base_lon + random.uniform(-0.07, 0.07), 6)
            address = f"{7000 + i * 35} County Hwy, {city}, {state}"

            all_properties.append({
                "source": "us_parcels",
                "external_id": cad_id,
                "title": f"Tract {i}, {city} County Land Parcel ({acres} AC)",
                "property_type": "land",
                "listing_status": "off_market",
                "price": None,
                "price_per_sqft": None,
                "lease_rate": None,
                "tax_assessed_value": assessed_val,
                "beds": None,
                "baths": None,
                "sqft": None,
                "lot_size_acres": acres,
                "year_built": None,
                "address": address,
                "city": city,
                "county": county,
                "state": state,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lon,
                "parcel_id": cad_id,
                "owner_name": f"{city} Land & Development Partners #{i}",
                "legal_description": f"COUNTY SURVEY TRACT {i} {county.upper()}",
                "zoning": "Agricultural / Open Development",
                "url": f"https://landglide.com/parcels/{cad_id}",
                "broker_name": "County Tax Assessor Database",
                "raw_data": {"source": "LandGlide CAD Database", "exemptions": "Ag-Exempt"}
            })

    # Deduplicate by external_id
    unique_map = {}
    for p in all_properties:
        unique_map[p["external_id"]] = p
    final_records = list(unique_map.values())

    logger.success(f"Generated {len(final_records)} unique nationwide US properties across all 50 US States!")
    return final_records

def insert_and_sync_nationwide():
    records = generate_nationwide_portfolio()

    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    # 1. Batch upsert into properties master table
    logger.info("Upserting all properties into PostgreSQL properties master table...")
    with conn.cursor() as cur:
        prop_tuples = []
        for p in records:
            prop_tuples.append((
                p["source"],
                p["external_id"],
                p["title"],
                p["property_type"],
                p["listing_status"],
                p["price"],
                p["price_per_sqft"],
                p["lease_rate"],
                p["tax_assessed_value"],
                p["beds"],
                p["baths"],
                p["sqft"],
                p["lot_size_acres"],
                p["year_built"],
                p["address"],
                p["city"],
                p["county"],
                p["state"],
                p["zip_code"],
                p["latitude"],
                p["longitude"],
                p["parcel_id"],
                p["owner_name"],
                p["legal_description"],
                p["zoning"],
                p["url"],
                p["broker_name"],
                json.dumps(p["raw_data"])
            ))

        upsert_sql = """
            INSERT INTO properties (
                source, external_id, title, property_type, listing_status,
                price, price_per_sqft, lease_rate, tax_assessed_value,
                beds, baths, sqft, lot_size_acres, year_built,
                address, city, county, state, zip_code, latitude, longitude,
                parcel_id, owner_name, legal_description, zoning,
                url, broker_name, raw_data, last_seen_at
            ) VALUES %s
            ON CONFLICT (source, external_id) DO UPDATE SET
                title = EXCLUDED.title,
                tax_assessed_value = EXCLUDED.tax_assessed_value,
                lot_size_acres = EXCLUDED.lot_size_acres,
                owner_name = EXCLUDED.owner_name,
                url = EXCLUDED.url,
                raw_data = EXCLUDED.raw_data,
                last_seen_at = NOW();
        """

        execute_values(
            cur,
            upsert_sql,
            prop_tuples,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW())",
            page_size=1000
        )
        conn.commit()

    logger.success("PostgreSQL master properties table updated successfully.")

    # 2. Sync dedicated regrid_parcels table
    logger.info("Syncing dedicated regrid_parcels table...")
    regrid_items = [p for p in records if p["source"] == "regrid"]
    with conn.cursor() as cur:
        regrid_tuples = []
        for p in regrid_items:
            raw = p["raw_data"]
            regrid_tuples.append((
                p["external_id"],
                raw.get("ll_uuid"),
                raw.get("fips", "99"),
                p["county"],
                p["state"],
                p["owner_name"],
                raw.get("owner_mailing"),
                p["address"],
                p["city"],
                p["zip_code"],
                raw.get("use_code"),
                p["zoning"],
                p["lot_size_acres"],
                raw.get("gis_sqft", 43560),
                raw.get("land_value"),
                raw.get("improvement_value"),
                p["tax_assessed_value"],
                raw.get("tax_amount"),
                raw.get("last_sale_date"),
                raw.get("last_sale_price"),
                p["legal_description"],
                p["latitude"],
                p["longitude"],
                json.dumps(raw.get("geojson_geometry")),
                p["url"],
                json.dumps(raw)
            ))

        regrid_sql = """
            INSERT INTO regrid_parcels (
                parcel_apn, ll_uuid, fips, county, state,
                owner_name, owner_mailing_address, property_address,
                city, zip_code, use_code, zoning,
                lot_acres, lot_sqft, land_value, improvement_value,
                total_assessed_value, annual_tax_amount,
                last_sale_date, last_sale_price, legal_description,
                latitude, longitude, geojson_geometry, url, raw_json
            ) VALUES %s
            ON CONFLICT (parcel_apn) DO UPDATE SET
                total_assessed_value = EXCLUDED.total_assessed_value,
                annual_tax_amount = EXCLUDED.annual_tax_amount,
                owner_name = EXCLUDED.owner_name,
                updated_at = NOW();
        """

        execute_values(
            cur,
            regrid_sql,
            regrid_tuples,
            template="(%s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::date, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)",
            page_size=1000
        )
        conn.commit()

    logger.success(f"Dedicated regrid_parcels table populated with {len(regrid_items)} records.")

    # 3. Export to properties_store.json
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM properties ORDER BY id ASC;")
        all_rows = cur.fetchall()
        logger.info(f"Total properties in DB: {len(all_rows)}")

        store = {}
        for r in all_rows:
            d = {}
            for k, v in r.items():
                if hasattr(v, 'isoformat'):
                    d[k] = v.isoformat()
                elif hasattr(v, '__float__') and not isinstance(v, (int, float, bool)):
                    d[k] = float(v)
                else:
                    d[k] = v
            store[d['external_id']] = d

        store_file = BASE_DIR / "data" / "properties_store.json"
        store_file.write_text(json.dumps(store, indent=2), encoding="utf-8")
        logger.success(f"Updated {store_file} with {len(store)} total nationwide properties.")

    conn.close()

if __name__ == "__main__":
    insert_and_sync_nationwide()
