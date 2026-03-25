from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from routers import pages, partials
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB connections, caches, etc.
    print(f"Starting {settings.app_name}...")
    yield
    # Shutdown: cleanup
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(partials.router, prefix="/partials")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
