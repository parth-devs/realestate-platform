import psycopg2
from config import settings

print(f"Connecting to host={settings.DB_HOST}, port={settings.DB_PORT}, dbname={settings.DB_NAME}, user={settings.DB_USER}")
try:
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        connect_timeout=3
    )
    print("SUCCESS: Connected to PostgreSQL successfully!")
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [t[0] for t in cur.fetchall()]
        print("Existing tables:", tables)
        if "properties" in tables:
            cur.execute("SELECT count(*) FROM properties;")
            count = cur.fetchone()[0]
            print(f"Total rows in 'properties' table: {count}")
    conn.close()
except Exception as e:
    print("Connection error:", e)
