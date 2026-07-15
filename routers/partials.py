from datetime import datetime
import logging
import json
import urllib.parse
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, Query, logger
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from dependencies import get_templates
from services.data_service import DataService
#from services.time_service import TimeService
from services.address_service import AddressProcessor, Address
from services.weather_service import WeatherProcessor, WeatherReading, TempUnit, SpeedUnit, weather_code

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["partials"])

# Each route here returns an HTML fragment consumed by HTMX.
# HTMX swaps these fragments into the DOM without a full page reload.
# route for the address service

# The cookie contains the last 10 searched locations
COOKIE_NAME = "recent_city_searches"
MAX_RECENT  = 10

def get_recent_searches(request: Request) -> list[str]:
    raw = request.cookies.get(COOKIE_NAME, "[]")
    try:
        return json.loads(urllib.parse.unquote(raw))
    except Exception:
        return []

def build_updated_searches(current: list[str], new_entry: str) -> list[str]:
    trimmed = new_entry.strip()
    updated = [s for s in current if s.lower() != trimmed.lower()]
    updated.insert(0, trimmed)
    return updated[:MAX_RECENT]

#load the weather from a cookie on load
@router.get("/weather-load", response_class=HTMLResponse)
async def weather_load(
    request: Request,
    city_state: Optional[str] = Query(default=None),
    timezone: Optional[str] = Query(default="UTC"),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Auto-loads weather on page ready using cookie value."""
    if city_state is None:
        return HTMLResponse(content="")  # nothing to load yet
    # get the 0th position from the get_recent_searches
    if city_state is None:
        recent_searches = get_recent_searches(request)
        if recent_searches:
            city_state = recent_searches[0]
    return await _get_weather_response(request, city_state, timezone, templates)


@router.post("/getWeatherForAddress", response_class=HTMLResponse)
async def get_weather_for_address(
    request: Request,
    city_state: Optional[str] = Form(None),
    timezone: Optional[str] = Form("UTC"),
    templates: Jinja2Templates = Depends(get_templates),
):
    """HTMX target: hx-post="/getWeatherForAddress" """
    recent  = get_recent_searches(request)
    updated = build_updated_searches(recent, city_state)

    response = await _get_weather_response(request, city_state, timezone, templates)
    response.set_cookie(
        key      = COOKIE_NAME,
        value    = urllib.parse.quote(json.dumps(updated)),
        max_age  = 60 * 60 * 24 * 365,  # 1 year
        httponly = False,   # False so JS can read it for the dropdown
        samesite = "lax",
    )
    #response.set_cookie(key="last_weather_location", value=city_state, max_age=60*60*24*30, httponly=True, samesite="lax")
    return response

async def _get_weather_response(
    request: Request,
    city_state: str,
    timezone: str,
    templates: Jinja2Templates,
) -> HTMLResponse:
    """Shared logic for fetching and rendering weather data."""
    logger.info("RF Processing weather request for address.")
    logger.debug(f"Received form data: city_state={city_state}, timezone={timezone}")
    aproc = AddressProcessor()
    wproc = WeatherProcessor()

    addressstring = Address.parse_address_s(city_state)
    if addressstring is None:
        logger.error("Failed to parse address information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )

    addressresponse = aproc.get_addressByPostalCode(Address(street="", city=addressstring.city, state=addressstring.state, zip_code=addressstring.zip_code, country=""))
    if addressresponse is None:
        logger.error("Failed to retrieve address information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )

    weather_address = Address.from_api_response(addressresponse[0])
    try:
        logger.debug(f"Fetching weather for address: {weather_address}, timezone: {timezone}")
        weather_response = wproc.get_current(weather_address, timezone)
    except RuntimeError as e:
        logger.error("Failed to retrieve weather information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": str(e)},
        )

    current_weather = WeatherReading.from_api_response(weather_response[0], weather_address)
    icon = WeatherProcessor().getweatherdescription(current_weather.weather_snapshot, weather_code.ICON)

    return templates.TemplateResponse(
        "partials/weather.html",
        {"request": request, "current_weather": current_weather, "icon": icon},
    )

#route for the time service
@router.get("/current_time", response_class=HTMLResponse)
async def current_time_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/current_time" hx-trigger="load" hx-target="#time-container"
    Returns the current time fragment.
    """

    #service = TimeService()
    #time_data = await service.get_current_time()
    time_data = datetime.now()

    return templates.TemplateResponse(
        "partials/current_time.html",
        {"request": request, "time_data": time_data.strftime("%Y-%m-%d")},
    )

#route for the reports page.
@router.get("/reports", response_class=HTMLResponse)
async def reports_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/reports" hx-target="#reports-container"
    Returns the reports fragment.
    """
    service = DataService()
    reports = await service.get_reports()

    return templates.TemplateResponse(
        "partials/reports.html",
        {"request": request, "reports": reports},
    )

@router.get("/stats", response_class=HTMLResponse)
async def stats_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/stats" hx-target="#stats-container"
    Returns the stats cards fragment.
    """
    service = DataService()
    stats = await service.get_stats()

    return templates.TemplateResponse(
        "partials/stats_card.html",
        {"request": request, "stats": stats},
    )


@router.get("/table", response_class=HTMLResponse)
async def table_partial(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/table?page=1" hx-target="#data-table"
    Supports pagination via query params — HTMX passes these automatically.
    """
    service = DataService()
    rows, total = await service.get_table_data(page=page, limit=limit)

    return templates.TemplateResponse(
        "partials/data_table.html",
        {
            "request": request,
            "rows": rows,
            "page": page,
            "total": total,
            "limit": limit,
        },
    )


@router.post("/item", response_class=HTMLResponse)
async def create_item_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-post="/partials/item" hx-target="#items-list" hx-swap="afterbegin"
    Creates an item and returns just the new row HTML to prepend.
    """
    form = await request.form()
    service = DataService()
    new_item = await service.create_item(dict(form))

    return templates.TemplateResponse(
        "partials/item_row.html",
        {"request": request, "item": new_item},
    )
