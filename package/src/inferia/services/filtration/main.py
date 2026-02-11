import uvicorn
from inferia.services.filtration.config import settings


def start_api():
    """Start the Filtration Service API."""
    uvicorn.run(
        "inferia.services.filtration.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    start_api()
