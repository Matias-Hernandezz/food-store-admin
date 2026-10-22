"""Geocodificación vía Nominatim (OpenStreetMap). Uso responsable: 1 req/s."""

import logging
from urllib.parse import urlencode

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def geocode_address(
    *,
    linea1: str,
    linea2: str | None = None,
    ciudad: str | None = None,
    provincia: str | None = None,
) -> tuple[float, float] | None:
    if not settings.geocoding_enabled:
        return None

    parts = [p.strip() for p in (linea1, linea2, ciudad, provincia, "Argentina") if p and str(p).strip()]
    if len(parts) < 2:
        return None

    query = ", ".join(parts)
    params = urlencode({"q": query, "format": "json", "limit": "1", "countrycodes": "ar"})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    headers = {"User-Agent": settings.geocoding_user_agent}

    try:
        with httpx.Client(timeout=settings.geocoding_timeout_seconds) as client:
            res = client.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
    except Exception as exc:
        logger.warning("Geocoding falló para '%s': %s", query, exc)
        return None

    if not data:
        return None

    try:
        lat = float(data[0]["lat"])
        lng = float(data[0]["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    return lat, lng
