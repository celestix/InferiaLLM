import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel
from inferia.services.guardrail.service_config import guardrail_settings

logger = logging.getLogger(__name__)


class GuardrailConfigManager:
    """
    Polls the Filtration Gateway for provider configuration.
    Updates local guardrail_settings.
    """

    _instance = None

    def __init__(self):
        self._polling_active = False
        self._task = None
        self.gateway_url = "http://localhost:8000"
        self.internal_api_key = ""  # Will be loaded from env via settings if possible

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GuardrailConfigManager()
        return cls._instance

    def _update_settings(self, providers: Dict[str, Any]):
        """Update local settings from gateway data."""
        guardrails = providers.get("guardrails", {})

        # Update Groq
        groq_key = guardrails.get("groq", {}).get("api_key")
        if groq_key:
            guardrail_settings.groq_api_key = groq_key

        # Update Lakera
        lakera_key = guardrails.get("lakera", {}).get("api_key")
        if lakera_key:
            guardrail_settings.lakera_api_key = lakera_key

        logger.debug("Guardrail settings updated from Gateway.")

    async def _poll_loop(self):
        logger.info("Starting configuration polling loop from Gateway...")
        headers = {}
        if (
            hasattr(guardrail_settings, "internal_api_key")
            and guardrail_settings.internal_api_key
        ):
            headers["X-Internal-API-Key"] = guardrail_settings.internal_api_key

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


config_manager = GuardrailConfigManager.get_instance()
