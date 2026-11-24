-- ==============================================================================
-- Complete Multi-Source Real Estate Database Schema for Texas
-- Dedicated Full-Schema Tables for Each Platform + Master View
-- ==============================================================================

-- 1. ZILLOW RESIDENTIAL FULL TABLE
CREATE TABLE IF NOT EXISTS zillow_residential (
    id BIGSERIAL PRIMARY KEY,
    zpid VARCHAR(100) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    county VARCHAR(100),
    state VARCHAR(10) DEFAULT 'TX',
    zip_code VARCHAR(20),
    price NUMERIC(14, 2),
    price_per_sqft NUMERIC(10, 2),
    beds NUMERIC(4, 1),
    baths NUMERIC(4, 1),
    sqft INTEGER,
    lot_size_acres NUMERIC(10, 4),
    year_built INTEGER,
    home_type VARCHAR(100),            -- single_family, condo, townhouse, multi_family
    listing_status VARCHAR(50) DEFAULT 'for_sale', -- for_sale, pending, sold, for_rent
    zestimate NUMERIC(14, 2),
    rent_zestimate NUMERIC(10, 2),
    days_on_zillow INTEGER,
    broker_name TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    url TEXT,
    raw_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zillow_city ON zillow_residential(city);
CREATE INDEX IF NOT EXISTS idx_zillow_price ON zillow_residential(price);
CREATE INDEX IF NOT EXISTS idx_zillow_beds_baths ON zillow_residential(beds, baths);


-- 2. LOOPNET COMMERCIAL FULL TABLE
CREATE TABLE IF NOT EXISTS loopnet_commercial (
    id BIGSERIAL PRIMARY KEY,
    loopnet_id VARCHAR(100) UNIQUE NOT NULL,
    title TEXT,
    property_type VARCHAR(100),        -- industrial, office, retail, commercial_land, multi_family
    listing_status VARCHAR(50) DEFAULT 'for_sale', -- for_sale, for_lease, under_contract
    price NUMERIC(14, 2),
    lease_rate TEXT,                   -- e.g. '$24 / SF / YR' or '$3,500 / MO'
    price_per_sqft NUMERIC(10, 2),
    building_sqft INTEGER,
    lot_acres NUMERIC(10, 4),
    cap_rate NUMERIC(6, 2),            -- Capitalization rate (%)
    noi NUMERIC(14, 2),                 -- Net Operating Income
    tenancy VARCHAR(50),               -- Single, Multi
    year_built INTEGER,
    address TEXT,
    city VARCHAR(100),
    county VARCHAR(100),
    state VARCHAR(10) DEFAULT 'TX',
    zip_code VARCHAR(20),
    submarket TEXT,
    broker_firm TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    url TEXT,
    raw_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_loopnet_type ON loopnet_commercial(property_type);
CREATE INDEX IF NOT EXISTS idx_loopnet_city ON loopnet_commercial(city);
CREATE INDEX IF NOT EXISTS idx_loopnet_price ON loopnet_commercial(price);


-- 3. LANDGLIDE & TEXAS COUNTY APPRAISAL DISTRICT (CAD) PARCEL TABLE
CREATE TABLE IF NOT EXISTS landglide_parcels (
    id BIGSERIAL PRIMARY KEY,
    parcel_apn VARCHAR(100) UNIQUE NOT NULL, -- Assessor Parcel Number
    county VARCHAR(100),                     -- Travis, Harris, Dallas, Bexar, etc.
    owner_name TEXT,
    owner_address TEXT,
    legal_description TEXT,                  -- Tract, Lot, Block, Section, Subdivision
    lot_acres NUMERIC(10, 4),
    lot_sqft INTEGER,
    land_assessed_value NUMERIC(14, 2),      -- County assessed land value
    improvement_value NUMERIC(14, 2),        -- Building/structure value
    total_assessed_value NUMERIC(14, 2),     -- Combined market valuation
    tax_exemptions TEXT,                     -- Homestead, Ag-Exempt, Over 65
    zoning VARCHAR(100),
    school_district VARCHAR(150),
    property_address TEXT,
    city VARCHAR(100),
    state VARCHAR(10) DEFAULT 'TX',
    zip_code VARCHAR(20),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    gis_polygon_coordinates JSONB,           -- Parcel boundary geometry
    raw_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_landglide_county ON landglide_parcels(county);
CREATE INDEX IF NOT EXISTS idx_landglide_owner ON landglide_parcels(owner_name);
CREATE INDEX IF NOT EXISTS idx_landglide_acres ON landglide_parcels(lot_acres);


-- 3b. REGRID NATIONWIDE PARCEL & BOUNDARY TABLE (regrid.com)
CREATE TABLE IF NOT EXISTS regrid_parcels (
    id BIGSERIAL PRIMARY KEY,
    parcel_apn VARCHAR(100) UNIQUE NOT NULL, -- Regrid parcelnumb
    ll_uuid UUID,                            -- Regrid Universal Unique ID
    fips VARCHAR(10),                        -- County FIPS code
    county VARCHAR(100),
    state VARCHAR(10) DEFAULT 'US',
    owner_name TEXT,                         -- Deed Owner
    owner_mailing_address TEXT,
    property_address TEXT,
    city VARCHAR(100),
    zip_code VARCHAR(20),
    use_code VARCHAR(150),                   -- Standardized Land Use
    zoning VARCHAR(100),
    lot_acres NUMERIC(10, 4),               -- Calculated GIS Acreage
    lot_sqft INTEGER,
    land_value NUMERIC(14, 2),
    improvement_value NUMERIC(14, 2),
    total_assessed_value NUMERIC(14, 2),    -- Total Assessment (Parval)
    annual_tax_amount NUMERIC(14, 2),
    last_sale_date DATE,
    last_sale_price NUMERIC(14, 2),
    legal_description TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    geojson_geometry JSONB,                 -- Exact parcel polygon boundary
    url TEXT,                                -- Direct Regrid App Link
    raw_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_regrid_county ON regrid_parcels(county);
CREATE INDEX IF NOT EXISTS idx_regrid_state ON regrid_parcels(state);
CREATE INDEX IF NOT EXISTS idx_regrid_owner ON regrid_parcels(owner_name);
CREATE INDEX IF NOT EXISTS idx_regrid_acres ON regrid_parcels(lot_acres);


-- 4. UNIFIED PROPERTIES MASTER TABLE
CREATE TABLE IF NOT EXISTS properties (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,            -- 'zillow', 'loopnet', 'texas_cad', 'landglide'
    external_id VARCHAR(100) NOT NULL,      -- ZPID, LoopNet ID, Parcel APN
    title TEXT,
    property_type VARCHAR(100),
    listing_status VARCHAR(50) DEFAULT 'active',
    price NUMERIC(14, 2),
    price_per_sqft NUMERIC(10, 2),
    lease_rate TEXT,
    tax_assessed_value NUMERIC(14, 2),
    beds NUMERIC(4, 1),
    baths NUMERIC(4, 1),
    sqft INTEGER,
    lot_size_acres NUMERIC(10, 4),
    year_built INTEGER,
    address TEXT,
    city VARCHAR(100),
    county VARCHAR(100),
    state VARCHAR(10) DEFAULT 'TX',
    zip_code VARCHAR(20),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    parcel_id VARCHAR(100),
    owner_name TEXT,
    legal_description TEXT,
    zoning VARCHAR(100),
    url TEXT,
    broker_name TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_source_external_id UNIQUE (source, external_id)
);

-- 5. PRICE HISTORY & AUDIT LOGS
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT REFERENCES properties(id) ON DELETE CASCADE,
    previous_price NUMERIC(14, 2),
    new_price NUMERIC(14, 2),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crawl_logs (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    target_area VARCHAR(100),
    items_scraped INTEGER DEFAULT 0,
    items_inserted INTEGER DEFAULT 0,
    items_updated INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);
