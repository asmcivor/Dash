from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def get_templates() -> Jinja2Templates:
    """Return the shared Jinja2 templates instance."""
    return templates


def is_htmx_request(request: Request) -> bool:
    """Check if the incoming request was triggered by HTMX."""
    return request.headers.get("HX-Request") == "true"
