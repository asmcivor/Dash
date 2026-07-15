from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi import Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from dependencies import get_templates
from services.data_service import DataService
from services.time_service import TimeService

router = APIRouter(tags=["pages"])

@router.get("/weather")
async def weather_detail(
    request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("pages/weatherdetail.html", {
        "request": request,
        "active_page": "weather",
    })

@router.get("/books")
async def books_detail(
    request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("pages/bookdetail.html", {
        "request": request,
        "active_page": "books",
    })

@router.get("/travel")
async def travel_detail(
    request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("pages/traveldetail.html", {
        "request": request,
        "active_page": "travel",
    })




@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    last_weather_location: Optional[str] = Cookie(default="Tualatin, OR")
):
    """Main dashboard page — renders the full HTML shell."""
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard", "last_weather_location": last_weather_location},
    )


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        "reports.html",
        {"request": request, "title": "Reports"},
    )

@router.get("/current_time", response_class=HTMLResponse)
async def current_time_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    
    return templates.TemplateResponse(
        "current_time.html",
        {"request": request, "title": "Current Time"},
    )