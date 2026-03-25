from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from dependencies import get_templates
from services.data_service import DataService
from services.time_service import TimeService

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """Main dashboard page — renders the full HTML shell."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard"},
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