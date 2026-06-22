#!/usr/bin/env python3
"""EVEZ-OS Geolocation Service — Free, no-key location APIs on port 9124.

Uses ip-api.com (free, no key) for IP geolocation.
Uses Nominatim/OpenStreetMap (free, no key) for reverse geocoding & nearby.
"""

import json
import time
import math
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

SPINE_URL = "http://localhost:9116/append"

def spine_log(domain, action, data):
    try:
        requests.post(SPINE_URL, json={"domain": domain, "action": action, "data": data, "timestamp": time.time()}, timeout=2)
    except Exception:
        pass

# ── Geolocation Functions ──────────────────────────────────────────

def locate_ip(ip=None):
    """Locate by IP using ip-api.com (free, no key, 45 req/min)."""
    url = f"http://ip-api.com/json/{ip or ''}?fields=66846719" if ip else "http://ip-api.com/json/?fields=66846719"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success":
            return {
                "status": "success",
                "ip": data.get("query"),
                "city": data.get("city"),
                "region": data.get("regionName"),
                "country": data.get("country"),
                "country_code": data.get("countryCode"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
                "zip": data.get("zip"),
            }
        else:
            return {"status": "error", "message": data.get("message", "lookup failed")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def reverse_geocode(lat, lon):
    """Reverse geocode using Nominatim (free, no key, 1 req/sec)."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 14, "addressdetails": 1},
            headers={"User-Agent": "EVEZ-OS-Geolocation/1.0"},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        address = data.get("address", {})
        return {
            "status": "success",
            "display_name": data.get("display_name"),
            "city": address.get("city") or address.get("town") or address.get("village"),
            "state": address.get("state"),
            "country": address.get("country"),
            "postcode": address.get("postcode"),
            "lat": lat,
            "lon": lon,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def find_nearby(lat, lon, radius_km=5):
    """Find nearby points of interest using Nominatim search (free, no key)."""
    nearby = []

    # Search for nearby amenities using Nominatim
    queries = [
        ("amenities", "amenity"),
        ("cafes", "cafe"),
        ("restaurants", "restaurant"),
        ("hospitals", "hospital"),
        ("schools", "school"),
        ("fuel", "fuel"),
    ]

    for label, _ in queries[:3]:  # Limit to 3 queries to respect rate limits
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": _,
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "limit": 5,
                    "viewbox": f"{lon-0.1},{lat+0.1},{lon+0.1},{lat-0.1}",
                    "bounded": 1,
                },
                headers={"User-Agent": "EVEZ-OS-Geolocation/1.0"},
                timeout=5,
            )
            if r.status_code == 200:
                results = r.json()
                for item in results:
                    item_lat = float(item.get("lat", 0))
                    item_lon = float(item.get("lon", 0))
                    dist = haversine_km(lat, lon, item_lat, item_lon)
                    nearby.append({
                        "name": item.get("display_name", "").split(",")[0],
                        "type": label,
                        "distance_km": round(dist, 2),
                        "lat": item_lat,
                        "lon": item_lon,
                    })
            time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
        except Exception:
            continue

    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby[:10]

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km using Haversine formula."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ── Cache ────────────────────────────────────────────────────────────

cache = {"last_locate": None, "last_nearby": None}

# ── HTTP Handler ─────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "geolocation", "port": 9124})
        elif self.path == "/nearby":
            # Use cached last location or default
            if cache["last_locate"] and cache["last_locate"].get("lat"):
                lat = cache["last_locate"]["lat"]
                lon = cache["last_locate"]["lon"]
                nearby = find_nearby(lat, lon)
                cache["last_nearby"] = nearby
                self._json(200, {"status": "success", "location": cache["last_locate"], "nearby": nearby})
            else:
                self._json(200, {"status": "no_location", "message": "POST /locate first to set a reference point, or provide lat/lon query params"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/health":
            self._json(200, {"status": "alive", "service": "geolocation", "port": 9124})
            return

        body = self._read_body()

        if self.path == "/locate":
            ip = body.get("ip")
            lat = body.get("lat")
            lon = body.get("lon")

            if ip:
                # Locate by IP
                result = locate_ip(ip)
                cache["last_locate"] = result
                spine_log("geolocation", "locate_ip", {"ip": ip})
                self._json(200, result)
            elif lat is not None and lon is not None:
                # Reverse geocode coordinates
                result = reverse_geocode(float(lat), float(lon))
                cache["last_locate"] = result
                spine_log("geolocation", "locate_coords", {"lat": lat, "lon": lon})
                self._json(200, result)
            else:
                # Auto-detect via server IP
                result = locate_ip()
                cache["last_locate"] = result
                spine_log("geolocation", "locate_auto", {})
                self._json(200, result)
        elif self.path == "/nearby":
            lat = body.get("lat")
            lon = body.get("lon")
            radius = body.get("radius_km", 5)

            if lat is None or lon is None:
                if cache["last_locate"] and cache["last_locate"].get("lat"):
                    lat = cache["last_locate"]["lat"]
                    lon = cache["last_locate"]["lon"]
                else:
                    self._json(400, {"error": "provide lat and lon, or POST /locate first"})
                    return

            nearby = find_nearby(float(lat), float(lon), float(radius))
            cache["last_nearby"] = nearby
            spine_log("geolocation", "nearby", {"lat": lat, "lon": lon, "count": len(nearby)})
            self._json(200, {"status": "success", "center": {"lat": lat, "lon": lon}, "radius_km": radius, "nearby": nearby})
        else:
            self._json(404, {"error": "not found"})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9124), Handler)
    print("📍 Geolocation Service running on :9124 — free, no-key APIs")
    server.serve_forever()
