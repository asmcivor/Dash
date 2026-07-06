from datetime import datetime
import logging
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
@router.post("/getWeatherForAddress", response_class=HTMLResponse)
async def LatLong_partial(
    request: Request,
    city_state: Optional[str] = Form(None),
    timezone: Optional[str] = Form("UTC"),
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/latlong
    Returns the address fragment for the given postal code.
    """
    """
    First get the address data from the form
    """
    logger.info("RF Processing weather request for address.")
    logger.debug(f"Received form data: city_state={city_state}, timezone={timezone}")
    aproc = AddressProcessor()
    wproc = WeatherProcessor()
    #addressresponse = aproc.get_addressByPostalCode(Address(street=street, city=city, state=state, zip_code=zip_code, country=country))
    addressstring = Address.parse_address_s(city_state)
    logger.debug(f"Parsed address string: {addressstring}")
    if addressstring is None:
        logger.error("Failed to parse address information.")
        addressdata = f"{city_state}."
        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )
    addressresponse = aproc.get_addressByPostalCode(Address(street="", city=addressstring.city, state=addressstring.state, zip_code=addressstring.zip_code, country=""))
    if addressresponse is None: 
        logger.error("Failed to retrieve address information.")
        addressdata = f"{city_state}."

        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )
# if data is ok then get the weather for the address
# At this point assuming only 1 address is returned from the address service, so we take the first one.
    weather_address = Address.from_api_response(addressresponse[0])
    try:
        logger.debug(f"Fetching weather for address: {weather_address}, timezone: {timezone}")
        weather_response = wproc.get_current(weather_address, timezone) 
    except RuntimeError as e:
        logger.error("Failed to retrieve weather information.")
        addressdata = f"{city_state}."
        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "error_message": str(e)},
        )
    current_weather = WeatherReading.from_api_response(weather_response[0], weather_address)
    # calculat the icon
    icon = WeatherProcessor().getweatherdescription(current_weather.weather_snapshot, weather_code.ICON)
    if current_weather is None:
        logger.error("Failed to retrieve weather information.")
        addressdata = f"{city_state}."
        
        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )
    
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
