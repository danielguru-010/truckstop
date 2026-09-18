from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from routes.services.fuel_optimizer import FuelCandidate


EARTH_RADIUS_MILES = 3958.8
DEFAULT_CORRIDOR_MILES = 25.0


@dataclass(frozen=True)
class LocatedStation:
    station_id: int
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    retail_price: object


def _great_circle_miles(first, second):
    latitude_one, longitude_one = map(radians, first)
    latitude_two, longitude_two = map(radians, second)
    latitude_delta = latitude_two - latitude_one
    longitude_delta = longitude_two - longitude_one
    haversine = (
        sin(latitude_delta / 2) ** 2
        + cos(latitude_one) * cos(latitude_two) * sin(longitude_delta / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(haversine))


def stations_on_route(route_geometry, stations, corridor_miles=DEFAULT_CORRIDOR_MILES):
    """Return stations near a GeoJSON route with distance measured along the route."""
    coordinates = route_geometry.get("coordinates", [])
    if len(coordinates) < 2:
        raise ValueError("Route geometry must contain at least two coordinates")

    route_points = [(latitude, longitude) for longitude, latitude in coordinates]
    segment_lengths = [
        _great_circle_miles(first, second)
        for first, second in zip(route_points, route_points[1:])
    ]
    cumulative_distances = [0.0]
    for segment_length in segment_lengths:
        cumulative_distances.append(cumulative_distances[-1] + segment_length)

    candidates = []
    for station in stations:
        if station.latitude is None or station.longitude is None:
            continue
        nearest_index, nearest_point = min(
            enumerate(route_points),
            key=lambda item: _great_circle_miles(
                item[1], (station.latitude, station.longitude)
            ),
        )
        distance_from_route = _great_circle_miles(
            nearest_point, (station.latitude, station.longitude)
        )
        if distance_from_route > corridor_miles:
            continue
        candidates.append(
            FuelCandidate(
                station_id=station.id,
                name=station.name,
                city=station.city,
                state=station.state,
                distance_miles=cumulative_distances[nearest_index],
                retail_price=station.retail_price,
            )
        )

    return sorted(candidates, key=lambda candidate: candidate.distance_miles)