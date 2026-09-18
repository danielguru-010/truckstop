import json

from django.http import JsonResponse
from routes.providers.routing import RoutingError
from routes.services.fuel_optimizer import FuelOptimizationError
from routes.services.route_planner import RoutePlanner


def health(request):
    return JsonResponse({"status": "ok"})


def plan_route(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are supported", "code": "method_not_allowed"},
            status=405,
            headers={"Allow": "POST"},
        )

    try:
        payload = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "Request body must be valid JSON", "code": "invalid_json"},
            status=400,
        )

    if not isinstance(payload, dict):
        return JsonResponse(
            {"error": "Request body must be a JSON object", "code": "invalid_body"},
            status=400,
        )

    start = payload.get("start")
    finish = payload.get("finish")
    if not isinstance(start, str) or not start.strip():
        return JsonResponse(
            {"error": "start must be a non-empty location string", "code": "invalid_start"},
            status=400,
        )
    if not isinstance(finish, str) or not finish.strip():
        return JsonResponse(
            {"error": "finish must be a non-empty location string", "code": "invalid_finish"},
            status=400,
        )

    try:
        result = RoutePlanner().plan(start.strip(), finish.strip())
    except (RoutingError, FuelOptimizationError, ValueError) as exc:
        return JsonResponse(
            {"error": str(exc), "code": "route_unavailable"},
            status=422,
        )

    result["total_cost"] = str(result["total_cost"])
    for stop in result["fuel_stops"]:
        stop["price_per_gallon"] = str(stop["price_per_gallon"])
        stop["cost"] = str(stop["cost"])
    return JsonResponse(result)
