import logging
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, Query, logger
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from dependencies import get_templates
from services.data_service import DataService
from services.time_service import TimeService
from services.address_service import AddressProcessor, Address
from services.weather_service import WeatherProcessor, WeatherReading, TempUnit, SpeedUnit

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["partials"])

# Each route here returns an HTML fragment consumed by HTMX.
# HTMX swaps these fragments into the DOM without a full page reload.
# route for the address service
@router.post("/getWeatherForAddress", response_class=HTMLResponse)
async def LatLong_partial(
    request: Request,
    street: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/latlong
    Returns the address fragment for the given postal code.
    """
    """
    First get the address data from the form
    """
    logger.debug(f"Received form data: street={street}, city={city}, state={state}, zip_code={zip_code}, country={country}")
    service = AddressProcessor()
    address = service.get_addressByPostalCode(Address(street=street, city=city, state=state, zip_code=zip_code, country=country))
    if address is None: 
        logger.error("Failed to retrieve address information.")
        addressdata = f"{street}, {city}, {state}, {zip_code}, {country}."
        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "addressdata": addressdata},
        )
# if data is ok then get the weather for the address
    currentWeather = WeatherProcessor().get_current(address)
    # calculat the icon
    icon = f"wi-day-sunny"
    if currentWeather is None:
        logger.error("Failed to retrieve weather information.")
        addressdata = f"{street}, {city}, {state}, {zip_code}, {country}."
        
        return templates.TemplateResponse(
            "partials/weatherError.html",   
            {"request": request, "addressdata": addressdata, "icon": icon},
        )
    
    return templates.TemplateResponse(
        "partials/weather.html",
        {"request": request, "currentWeather": currentWeather, "icon": icon},
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

    service = TimeService()
    time_data = await service.get_current_time()

    return templates.TemplateResponse(
        "partials/current_time.html",
        {"request": request, "time_data": time_data},
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
