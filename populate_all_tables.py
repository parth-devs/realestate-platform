import psycopg2
from loguru import logger
from config import settings

def sync_dedicated_tables_from_db():
    logger.info("Synchronizing dedicated platform tables directly from PostgreSQL master table...")
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    with conn.cursor() as cur:
        # 1. Sync zillow_residential from properties
        logger.info("Syncing zillow_residential with DISTINCT ON (zpid)...")
        cur.execute("""
            INSERT INTO zillow_residential (
                zpid, address, city, county, state, zip_code,
                price, price_per_sqft, beds, baths, sqft, lot_size_acres, year_built,
                home_type, listing_status, broker_name, latitude, longitude, url, raw_json
            )
            SELECT DISTINCT ON (external_id)
                external_id, address, city, county, state, zip_code,
                price, price_per_sqft, beds, baths, sqft, lot_size_acres, year_built,
                property_type, listing_status, broker_name, latitude, longitude, url, raw_data
            FROM properties
            WHERE source = 'zillow'
            ORDER BY external_id, updated_at DESC
            ON CONFLICT (zpid) DO UPDATE SET
                price = EXCLUDED.price,
                beds = EXCLUDED.beds,
                baths = EXCLUDED.baths,
                sqft = EXCLUDED.sqft,
                updated_at = NOW();
        """)

        # 2. Sync loopnet_commercial from properties
        logger.info("Syncing loopnet_commercial with DISTINCT ON (loopnet_id)...")
        cur.execute("""
            INSERT INTO loopnet_commercial (
                loopnet_id, title, property_type, listing_status,
                price, lease_rate, price_per_sqft, building_sqft, lot_acres,
                address, city, county, state, zip_code, broker_firm, latitude, longitude, url, raw_json
            )
            SELECT DISTINCT ON (external_id)
                external_id, title, property_type, listing_status,
                price, lease_rate, price_per_sqft, sqft, lot_size_acres,
                address, city, county, state, zip_code, broker_name, latitude, longitude, url, raw_data
            FROM properties
            WHERE source = 'loopnet'
            ORDER BY external_id, updated_at DESC
            ON CONFLICT (loopnet_id) DO UPDATE SET
                price = EXCLUDED.price,
                lease_rate = EXCLUDED.lease_rate,
                updated_at = NOW();
        """)

        # 3. Sync landglide_parcels from properties
        logger.info("Syncing landglide_parcels with DISTINCT ON (parcel_apn)...")
        cur.execute("""
            INSERT INTO landglide_parcels (
                parcel_apn, county, owner_name, legal_description,
                lot_acres, total_assessed_value, zoning,
                property_address, city, state, zip_code, latitude, longitude, raw_json
            )
            SELECT DISTINCT ON (external_id)
                external_id, county, owner_name, legal_description,
                lot_size_acres, tax_assessed_value, zoning,
                address, city, state, zip_code, latitude, longitude, raw_data
            FROM properties
            WHERE source IN ('texas_cad', 'landglide', 'us_parcels')
            ORDER BY external_id, updated_at DESC
            ON CONFLICT (parcel_apn) DO UPDATE SET
                total_assessed_value = EXCLUDED.total_assessed_value,
                owner_name = EXCLUDED.owner_name,
                updated_at = NOW();
        """)

        conn.commit()

        # Print live summary
        cur.execute("""
            SELECT 'zillow_residential' AS table_name, count(*) FROM zillow_residential
            UNION ALL
            SELECT 'loopnet_commercial', count(*) FROM loopnet_commercial
            UNION ALL
            SELECT 'landglide_parcels', count(*) FROM landglide_parcels
            UNION ALL
            SELECT 'properties (MASTER ALL US)', count(*) FROM properties;
        """)
        counts = cur.fetchall()
        print("\n" + "="*60)
        print("DATABASE SUMMARY ACROSS ALL DEDICATED TABLES:")
        print("="*60)
        for t, c in counts:
            print(f"Table: {t:<30} | Total Rows: {c}")
        print("="*60 + "\n")

    conn.close()

if __name__ == "__main__":
    sync_dedicated_tables_from_db()
