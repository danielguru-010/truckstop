from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


MAX_RANGE_MILES = 500.0
MILES_PER_GALLON = 10.0
_CURRENCY_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class FuelCandidate:
    station_id: int
    name: str
    city: str
    state: str
    distance_miles: float
    retail_price: Decimal


@dataclass(frozen=True)
class FuelStop:
    station_id: int
    name: str
    city: str
    state: str
    distance_miles: float
    price_per_gallon: Decimal
    gallons: float
    cost: Decimal


@dataclass(frozen=True)
class FuelPlan:
    stops: tuple[FuelStop, ...]
    total_gallons: float
    total_cost: Decimal


class FuelOptimizationError(Exception):
    """Raised when no feasible fuel plan exists for a route."""


def optimize_fuel_stops(
    route_distance_miles: float,
    candidates: list[FuelCandidate],
    max_range_miles: float = MAX_RANGE_MILES,
    miles_per_gallon: float = MILES_PER_GALLON,
) -> FuelPlan:
    if route_distance_miles < 0 or max_range_miles <= 0 or miles_per_gallon <= 0:
        raise ValueError("Route distance, range, and fuel economy must be positive")
    if route_distance_miles == 0:
        return FuelPlan(stops=(), total_gallons=0.0, total_cost=Decimal("0.00"))

    stations = sorted(
        (candidate for candidate in candidates if 0 < candidate.distance_miles < route_distance_miles),
        key=lambda candidate: candidate.distance_miles,
    )
    points = [None, *stations, None]
    distances = [0.0, *(station.distance_miles for station in stations), route_distance_miles]
    for previous, current in zip(distances, distances[1:]):
        if current - previous > max_range_miles:
            raise FuelOptimizationError("No fuel station is reachable within the vehicle range")

    fuel_miles = max_range_miles
    stops = []
    total_gallons = 0.0
    total_cost = Decimal("0.00")
    current_index = 0

    while current_index < len(points) - 1:
        current_distance = distances[current_index]
        current_station = points[current_index]
        next_station_index = current_index + 1

        if current_station is None:
            next_station_index = 1
        else:
            for index in range(current_index + 1, len(points)):
                distance_to_station = distances[index] - current_distance
                if distance_to_station > max_range_miles:
                    break
                if points[index] is not None and points[index].retail_price < current_station.retail_price:
                    next_station_index = index
                    break
                next_station_index = index

        target_distance = distances[next_station_index]
        miles_to_target = target_distance - current_distance
        fuel_needed = max(0.0, miles_to_target - fuel_miles)
        if current_station is not None and fuel_needed > 0:
            gallons = fuel_needed / miles_per_gallon
            cost = (current_station.retail_price * Decimal(str(gallons))).quantize(
                _CURRENCY_PLACES, rounding=ROUND_HALF_UP
            )
            stops.append(
                FuelStop(
                    station_id=current_station.station_id,
                    name=current_station.name,
                    city=current_station.city,
                    state=current_station.state,
                    distance_miles=current_distance,
                    price_per_gallon=current_station.retail_price,
                    gallons=gallons,
                    cost=cost,
                )
            )
            total_gallons += gallons
            total_cost += cost
            fuel_miles += fuel_needed

        fuel_miles -= miles_to_target
        current_index = next_station_index

    return FuelPlan(
        stops=tuple(stops),
        total_gallons=total_gallons,
        total_cost=total_cost.quantize(_CURRENCY_PLACES),
    )