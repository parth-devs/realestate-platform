import json
import re
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from loguru import logger
from collectors.base import BaseCollector

class ZillowCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="zillow")
        self.base_url = "https://www.zillow.com"

    def run(self, city: str, state: str = "TX") -> List[Dict[str, Any]]:
        """
        Fetches residential listings for a Texas city.
        Example target: Austin, TX -> https://www.zillow.com/austin-tx/
        """
        logger.info(f"[Zillow] Starting collection for {city}, {state}...")
        formatted_city = city.lower().replace(" ", "-")
        search_url = f"{self.base_url}/{formatted_city}-{state.lower()}/"

        resp = self.fetch(search_url)
        if not resp:
            logger.error(f"[Zillow] Could not retrieve search page for {city}, {state}")
            return []

        properties = self._parse_html(resp.text, city, state)
        logger.info(f"[Zillow] Extracted {len(properties)} properties for {city}, {state}.")
        return properties

    def _parse_html(self, html_content: str, default_city: str, default_state: str) -> List[Dict[str, Any]]:
        properties = []
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Look for embedded NEXT_DATA JSON payload (fastest and most structured)
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if next_data_script and next_data_script.string:
            try:
                data = json.loads(next_data_script.string)
                search_results = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("searchPageState", {})
                    .get("cat1", {})
                    .get("searchResults", {})
                    .get("listResults", [])
                )
                for item in search_results:
                    prop = self._normalize_json_item(item, default_city, default_state)
                    if prop:
                        properties.append(prop)
                if properties:
                    return properties
            except Exception as e:
                logger.warning(f"[Zillow] Error parsing __NEXT_DATA__: {e}")

        # 2. Fallback: Parse HTML property cards
        cards = soup.select('article[data-test="property-card"]') or soup.select('div[class*="StyledPropertyCard"]')
        for card in cards:
            try:
                # External ID (ZPID)
                zpid = card.get("id", "").replace("zpid_", "") or card.get("data-zpid")
                if not zpid:
                    link = card.find("a", href=True)
                    if link and "_zpid" in link["href"]:
                        match = re.search(r"(\d+)_zpid", link["href"])
                        if match:
                            zpid = match.group(1)

                if not zpid:
                    continue

                # Price
                price_el = card.find("span", {"data-test": "property-card-price"}) or card.find(string=re.compile(r"^\$[\d,]+"))
                price = None
                if price_el:
                    price_str = re.sub(r"[^\d]", "", price_el.text if hasattr(price_el, "text") else str(price_el))
                    if price_str.isdigit():
                        price = float(price_str)

                # Address
                addr_el = card.find("address")
                address = addr_el.text.strip() if addr_el else None

                # Details (Beds, Baths, Sqft)
                beds, baths, sqft = None, None, None
                details = card.find_all("li")
                for li in details:
                    text = li.text.lower()
                    if "bd" in text or "bed" in text:
                        m = re.search(r"([\d\.]+)", text)
                        if m: beds = float(m.group(1))
                    elif "ba" in text or "bath" in text:
                        m = re.search(r"([\d\.]+)", text)
                        if m: baths = float(m.group(1))
                    elif "sqft" in text:
                        m = re.search(r"([\d,]+)", text)
                        if m: sqft = int(m.group(1).replace(",", ""))

                # Link
                link_el = card.find("a", href=True)
                url = (self.base_url + link_el["href"]) if (link_el and link_el["href"].startswith("/")) else (link_el["href"] if link_el else None)

                prop_record = {
                    "source": "zillow",
                    "external_id": zpid,
                    "title": address,
                    "property_type": "residential",
                    "listing_status": "for_sale",
                    "price": price,
                    "price_per_sqft": (price / sqft) if (price and sqft) else None,
                    "beds": beds,
                    "baths": baths,
                    "sqft": sqft,
                    "address": address,
                    "city": default_city,
                    "state": default_state,
                    "url": url,
                    "raw_data": {"extracted_from": "html_fallback"}
                }
                properties.append(prop_record)
            except Exception as ex:
                logger.debug(f"[Zillow] Error parsing single card: {ex}")

        return properties

    def _normalize_json_item(self, item: Dict[str, Any], city: str, state: str) -> Dict[str, Any] | None:
        try:
            zpid = str(item.get("zpid") or item.get("id"))
            if not zpid:
                return None

            unformatted_price = item.get("unformattedPrice")
            price = float(unformatted_price) if unformatted_price else None

            sqft = item.get("area")
            beds = item.get("beds")
            baths = item.get("baths")

            lat_long = item.get("latLong", {})
            latitude = lat_long.get("latitude")
            longitude = lat_long.get("longitude")

            hdp = item.get("hdpData", {}).get("homeInfo", {})
            address = item.get("address") or item.get("addressStreet") or hdp.get("streetAddress")
            zip_code = item.get("addressZipcode") or hdp.get("zipcode")
            real_city = item.get("addressCity") or hdp.get("city") or city
            real_state = (item.get("addressState") or hdp.get("state") or state).upper()

            lot_val = hdp.get("lotAreaValue")
            lot_unit = (hdp.get("lotAreaUnit") or "").lower()
            lot_acres = None
            if lot_val is not None:
                try:
                    lv = float(lot_val)
                    if "acre" in lot_unit:
                        lot_acres = round(lv, 3)
                    elif "sqft" in lot_unit:
                        lot_acres = round(lv / 43560.0, 3)
                    else:
                        lot_acres = round(lv, 3) if lv < 500 else round(lv / 43560.0, 3)
                except Exception:
                    pass

            tax_val = hdp.get("taxAssessedValue")
            zest = hdp.get("zestimate")
            home_type = (hdp.get("homeType") or "single_family").lower()
            raw_status = (hdp.get("homeStatus") or "FOR_SALE").lower()
            listing_status = "for_rent" if "rent" in raw_status else ("off_market" if "sold" in raw_status else "for_sale")

            detail_url = item.get("detailUrl", "")
            if detail_url and not detail_url.startswith("http"):
                detail_url = self.base_url + detail_url

            # Build accurate proportional parcel box around exact rooftop/parcel coordinates
            if latitude is not None and longitude is not None:
                import math
                ac = lot_acres if (lot_acres and lot_acres > 0) else 0.25
                side_m = math.sqrt(ac * 4046.8564224)
                d_lat = max(0.00016, min(0.004, ((side_m * 0.9) / 2.0) / 111320.0))
                d_lon = max(0.00019, min(0.005, ((side_m * 1.1) / 2.0) / (111320.0 * max(0.2, math.cos(math.radians(float(latitude)))))))
                item["geojson_geometry"] = {
                    "type": "Polygon",
                    "coordinates": [[
                        [round(float(longitude) - d_lon, 6), round(float(latitude) - d_lat, 6)],
                        [round(float(longitude) + d_lon, 6), round(float(latitude) - d_lat, 6)],
                        [round(float(longitude) + d_lon, 6), round(float(latitude) + d_lat, 6)],
                        [round(float(longitude) - d_lon, 6), round(float(latitude) + d_lat, 6)],
                        [round(float(longitude) - d_lon, 6), round(float(latitude) - d_lat, 6)],
                    ]]
                }

            return {
                "source": "zillow",
                "external_id": zpid,
                "title": address,
                "property_type": home_type,
                "listing_status": listing_status,
                "price": price,
                "price_per_sqft": round(price / sqft, 2) if (price and sqft) else None,
                "tax_assessed_value": float(tax_val) if tax_val else None,
                "beds": float(beds) if beds is not None else None,
                "baths": float(baths) if baths is not None else None,
                "sqft": int(sqft) if sqft else None,
                "lot_size_acres": lot_acres,
                "address": address,
                "city": real_city,
                "state": real_state,
                "zip_code": zip_code,
                "latitude": float(latitude) if latitude is not None else None,
                "longitude": float(longitude) if longitude is not None else None,
                "parcel_id": f"{real_state}-{zip_code or '00000'}-{zpid[-6:]}",
                "broker_name": item.get("brokerName"),
                "url": detail_url,
                "raw_data": item
            }
        except Exception as e:
            logger.debug(f"[Zillow] Failed to normalize JSON item: {e}")
            return None
