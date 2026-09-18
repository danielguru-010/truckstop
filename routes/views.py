import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from routes.providers.routing import RoutingError
from routes.services.fuel_optimizer import FuelOptimizationError
from routes.services.route_planner import RoutePlanner


def health(request):
    return JsonResponse({"status": "ok"})


@require_POST
def plan_route(request):
    try:
        payload = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Request body must be a JSON object"}, status=400)

    start = payload.get("start")
    finish = payload.get("finish")
    if not isinstance(start, str) or not start.strip():
        return JsonResponse({"error": "start must be a non-empty location string"}, status=400)
    if not isinstance(finish, str) or not finish.strip():
        return JsonResponse({"error": "finish must be a non-empty location string"}, status=400)

    try:
        result = RoutePlanner().plan(start.strip(), finish.strip())
    except (RoutingError, FuelOptimizationError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=422)

    result["total_cost"] = str(result["total_cost"])
    for stop in result["fuel_stops"]:
        stop["price_per_gallon"] = str(stop["price_per_gallon"])
        stop["cost"] = str(stop["cost"])
    return JsonResponse(result)
