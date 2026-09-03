"""Public IP, ASN, and Geolocation lookup module."""

import urllib.request
import json
from typing import Dict, Any, Optional


def fetch_ip_info(ip: Optional[str] = None, timeout: float = 3.0) -> Dict[str, Any]:
    """Fetch public IP metadata and ASN information."""
    url = f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/"
    headers = {"User-Agent": "NetPulse-CLI/1.0"}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return {
                    "ip": data.get("ip"),
                    "city": data.get("city"),
                    "region": data.get("region"),
                    "country": data.get("country_name"),
                    "country_code": data.get("country_code"),
                    "org": data.get("org"),
                    "asn": data.get("asn"),
                    "timezone": data.get("timezone"),
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude")
                }
    except Exception:
        # Fallback to ipify for raw IP if ipapi rate-limited
        try:
            req_fallback = urllib.request.Request("https://api.ipify.org?format=json", headers=headers)
            with urllib.request.urlopen(req_fallback, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                return {"ip": data.get("ip"), "country": "Unknown (Fallback)", "org": "N/A"}
        except Exception:
            pass

    return {
        "ip": "Offline / Unreachable",
        "city": "Unknown",
        "country": "Unknown",
        "org": "Unknown"
    }
