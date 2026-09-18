# Truck Stop Fuel Planner

API for planning cost-effective fuel stops along routes in the United States.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

The initial health endpoint is available at `GET /health/`.

## Import fuel prices

Apply the database migration and import the supplied assessment data with:

```bash
python manage.py migrate
python manage.py import_fuel_prices /path/to/fuel-prices-for-be-assessment.csv
```

The import is safe to run again: existing station rows are updated rather than duplicated.

## Routing providers

The API uses Nominatim for US location geocoding and the public OSRM service for driving routes.
Both provider URLs, the request timeout, and the required User-Agent can be configured with
`GEOCODING_BASE_URL`, `ROUTING_BASE_URL`, `ROUTING_TIMEOUT_SECONDS`, and `ROUTING_USER_AGENT`.
