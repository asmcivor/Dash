from fastapi import FastAPI
from fastapi.staticfiles import  StaticFiles
import logging  
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


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) 
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("Logging is set up.")

setup_logging()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# Static files

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(partials.router, prefix="/partials")

#for route in app.routes:
#    print(route.path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
