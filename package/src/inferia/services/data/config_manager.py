import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from inferia.services.data.config import settings

logger = logging.getLogger(__name__)


class DataConfigManager:
    """
    Polls the Filtration Gateway for provider configuration.
    Updates local data settings (Vectordb, OpenAI for prompt).
    """

    _instance = None

    def __init__(self):
        self._polling_active = False
        self._task = None
        self.gateway_url = "http://localhost:8000"
        self.internal_api_key = ""

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DataConfigManager()
        return cls._instance

    def _update_settings(self, providers: Dict[str, Any]):
        """Update local settings from gateway data."""
        # 1. Update Vectordb
        vectordb = providers.get("vectordb", {})
        chroma = vectordb.get("chroma", {})

        if chroma:
            settings.providers.vectordb.chroma.api_key = chroma.get("api_key")
            settings.providers.vectordb.chroma.url = chroma.get("url")
            settings.providers.vectordb.chroma.tenant = chroma.get("tenant")
            settings.providers.vectordb.chroma.database = chroma.get("database")
            settings.providers.vectordb.chroma.is_local = chroma.get("is_local", True)

            # Re-initialize engine client if URL changed
            try:
                from inferia.services.data.engine import data_engine

                data_engine.initialize_client()
            except Exception as e:
                logger.error(f"Failed to re-initialize data engine: {e}")

        # 2. Update OpenAI (for prompt rewriting)
        # Note: In monolith, we used guardrails groq or something?
        # Actually filtration/config has guardrails.groq.
        # Data service might want its own or reuse.
        # Gateway sends all providers.

        guardrails = providers.get("guardrails", {})
        groq_key = guardrails.get("groq", {}).get("api_key")
        if groq_key:
            # If data service uses groq for something
            pass

        # Check for OpenAI if we added it specifically for Data service
        # For now, just logging.
        logger.debug("Data settings updated from Gateway.")

    async def _poll_loop(self):
        logger.info("Starting configuration polling loop from Gateway...")
        headers = {}
        if hasattr(settings, "internal_api_key") and settings.internal_api_key:
            headers["X-Internal-API-Key"] = settings.internal_api_key

        while self._polling_active:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.gateway_url}/internal/config/provider",
                        headers=headers,
                        timeout=5.0,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "providers" in data:
                            self._update_settings(data["providers"])
                    else:
                        logger.warning(
                            f"Failed to fetch config from Gateway: {response.status_code}"
                        )
            except Exception as e:
                logger.error(f"Error polling Gateway configuration: {e}")

            await asyncio.sleep(15)

    def start_polling(
        self, gateway_url: str = "http://localhost:8000", api_key: str = ""
    ):
        if self._polling_active:
            return

        self.gateway_url = gateway_url
        self.internal_api_key = api_key
        self._polling_active = True
        self._task = asyncio.create_task(self._poll_loop())

    def stop_polling(self):
        self._polling_active = False
        if self._task:
            self._task.cancel()


config_manager = DataConfigManager.get_instance()
