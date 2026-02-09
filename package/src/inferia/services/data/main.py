import uvicorn
from inferia.services.data.config import settings


def start_api():
    """Start the Data Service API."""
    uvicorn.run(
        "inferia.services.data.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    start_api()
