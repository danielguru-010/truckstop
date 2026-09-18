import json
from hashlib import sha256
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Route:
    distance_miles: float
    duration_seconds: float
    geometry: dict


class RoutingError(Exception):
    """Raised when a routing or geocoding provider cannot answer a request."""


class RoutingProvider:
    def _get_json(self, url):
        request = Request(
            url,
            headers={"User-Agent": settings.ROUTING_USER_AGENT},
        )
        try:
            with urlopen(request, timeout=settings.ROUTING_TIMEOUT_SECONDS) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RoutingError(f"Routing provider request failed: {exc}") from exc


class NominatimGeocoder(RoutingProvider):
    def geocode(self, location):
        normalized_location = location.strip().lower()
        location_hash = sha256(normalized_location.encode()).hexdigest()
        cache_key = f"route-geocode:v1:{location_hash}"
        cached = cache.get(cache_key)
        if cached:
            return Coordinate(**cached)

        url = (
            f"{settings.GEOCODING_BASE_URL}/search"
            f"?q={quote(location)}&format=jsonv2&limit=1&countrycodes=us"
        )
        results = self._get_json(url)
        if not results:
            raise RoutingError(f"Location could not be found: {location}")

        try:
            coordinate = Coordinate(
                latitude=float(results[0]["lat"]),
                longitude=float(results[0]["lon"]),
            )
            cache.set(cache_key, coordinate.__dict__, settings.ROUTING_CACHE_TTL_SECONDS)
            return coordinate
        except (KeyError, TypeError, ValueError) as exc:
            raise RoutingError("Geocoding provider returned an invalid location") from exc


class OsrmRouter(RoutingProvider):
    def route(self, start, finish):
        cache_key = (
            f"route-osrm:v1:{start.latitude:.6f}:{start.longitude:.6f}:"
            f"{finish.latitude:.6f}:{finish.longitude:.6f}"
        )
        cached = cache.get(cache_key)
        if cached:
            return Route(**cached)

        coordinates = f"{start.longitude},{start.latitude};{finish.longitude},{finish.latitude}"
        url = (
            f"{settings.ROUTING_BASE_URL}/route/v1/driving/{coordinates}"
            "?overview=full&geometries=geojson"
        )
        response = self._get_json(url)
        if response.get("code") != "Ok" or not response.get("routes"):
            raise RoutingError("Routing provider did not return a route")

        route = response["routes"][0]
        try:
            route_result = Route(
                distance_miles=float(route["distance"]) / 1609.344,
                duration_seconds=float(route["duration"]),
                geometry=route["geometry"],
            )
            cache.set(cache_key, route_result.__dict__, settings.ROUTING_CACHE_TTL_SECONDS)
            return route_result
        except (KeyError, TypeError, ValueError) as exc:
            raise RoutingError("Routing provider returned an invalid route") from exc