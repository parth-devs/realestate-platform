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

            address = item.get("address") or item.get("addressStreet")
            zip_code = item.get("addressZipcode")

            detail_url = item.get("detailUrl", "")
            if detail_url and not detail_url.startswith("http"):
                detail_url = self.base_url + detail_url

            return {
                "source": "zillow",
                "external_id": zpid,
                "title": address,
                "property_type": item.get("hdpData", {}).get("homeInfo", {}).get("homeType", "single_family").lower(),
                "listing_status": "for_sale",
                "price": price,
                "price_per_sqft": (price / sqft) if (price and sqft) else None,
                "beds": float(beds) if beds is not None else None,
                "baths": float(baths) if baths is not None else None,
                "sqft": int(sqft) if sqft else None,
                "address": address,
                "city": item.get("addressCity") or city,
                "state": state,
                "zip_code": zip_code,
                "latitude": latitude,
                "longitude": longitude,
                "broker_name": item.get("brokerName"),
                "url": detail_url,
                "raw_data": item
            }
        except Exception as e:
            logger.debug(f"[Zillow] Failed to normalize JSON item: {e}")
            return None
