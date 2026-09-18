from dataclasses import asdict

from routes.models import FuelStation
from routes.providers.routing import NominatimGeocoder, OsrmRouter
from routes.services.fuel_optimizer import optimize_fuel_stops
from routes.services.route_candidates import stations_on_route


class RoutePlanner:
    def __init__(self, geocoder=None, router=None):
        self.geocoder = geocoder or NominatimGeocoder()
        self.router = router or OsrmRouter()

    def plan(self, start_location, finish_location):
        start = self.geocoder.geocode(start_location)
        finish = self.geocoder.geocode(finish_location)
        route = self.router.route(start, finish)
        stations = FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
        ).only(
            "id",
            "name",
            "city",
            "state",
            "latitude",
            "longitude",
            "retail_price",
        )
        candidates = stations_on_route(route.geometry, stations)
        fuel_plan = optimize_fuel_stops(route.distance_miles, candidates)

        return {
            "route": {
                "distance_miles": route.distance_miles,
                "duration_seconds": route.duration_seconds,
                "geometry": route.geometry,
            },
            "fuel_stops": [asdict(stop) for stop in fuel_plan.stops],
            "total_gallons": fuel_plan.total_gallons,
            "total_cost": fuel_plan.total_cost,
        }