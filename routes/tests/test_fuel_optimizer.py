from decimal import Decimal

from django.test import SimpleTestCase

from routes.services.fuel_optimizer import (
    FuelCandidate,
    FuelOptimizationError,
    optimize_fuel_stops,
)


def station(station_id, distance_miles, price):
    return FuelCandidate(
        station_id=station_id,
        name=f"Station {station_id}",
        city="Test City",
        state="OK",
        distance_miles=distance_miles,
        retail_price=Decimal(price),
    )


class FuelOptimizerTests(SimpleTestCase):
    def test_stops_at_cheaper_reachable_station(self):
        plan = optimize_fuel_stops(
            route_distance_miles=700,
            candidates=[station(1, 300, "4.00"), station(2, 450, "3.00")],
        )

        self.assertEqual([stop.station_id for stop in plan.stops], [2])
        self.assertEqual(plan.total_gallons, 20.0)
        self.assertEqual(plan.total_cost, Decimal("60.00"))

    def test_does_not_stop_when_initial_fuel_reaches_destination(self):
        plan = optimize_fuel_stops(400, [station(1, 200, "3.00")])

        self.assertEqual(plan.stops, ())
        self.assertEqual(plan.total_cost, Decimal("0.00"))

    def test_rejects_route_with_unreachable_gap(self):
        with self.assertRaises(FuelOptimizationError):
            optimize_fuel_stops(1100, [station(1, 600, "3.00")])