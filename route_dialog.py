"""
TRINITY ROUTE: DIALOGFLOW CX
============================
Dialogflow CX as a free conversational AI route.
Leverages Dialogflow CX free tier to handle conversational queries
with multi-project failover and in-memory credential management.

Supports both Base64-encoded Service Account JSON Keys
and Google Cloud Application Default Credentials (ADC).
"""

import os
import json
import base64
from typing import Any, Dict, List

from dotenv import load_dotenv
from loguru import logger
from google.cloud.dialogflowcx_v3.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3.types import session
from google.oauth2 import service_account

load_dotenv()


class DialogflowRoute:
    """Encapsulates a Dialogflow CX route with credential management."""

    def __init__(self, config: Dict[str, Any]):
        self.name: str = config.get("name", "Dialog Route")
        self.project_id: str | None = config.get("project_id")
        self.agent_id: str | None = config.get("agent_id")
        self.location: str = config.get("location", "us-central1")
        self.language_code: str = config.get("language_code", "fr")
        self.key_b64: str | None = config.get("key_b64")

        if not self.project_id or not self.agent_id:
            raise ValueError(f"[{self.name}] Missing required config: project_id or agent_id.")

    def _build_client(self) -> SessionsClient:
        """Initializes the Dialogflow CX client.

        Uses in-memory credentials from Base64 key if provided,
        otherwise falls back to Application Default Credentials (ADC).
        """
        client_options = {
            "api_endpoint": f"{self.location}-dialogflow.googleapis.com:443"
        }

        if self.key_b64:
            key_info = json.loads(base64.b64decode(self.key_b64).decode("utf-8"))
            creds = service_account.Credentials.from_service_account_info(key_info)
            logger.debug(f"[{self.name}] Using provided Base64 Service Account Key (in-memory).")
            return SessionsClient(credentials=creds, client_options=client_options)

        logger.debug(f"[{self.name}] No Base64 Key provided. Relying on Application Default Credentials (ADC).")
        return SessionsClient(client_options=client_options)

    def query(self, text: str, session_id: str = "default") -> str:
        """Execute Dialogflow CX detect intent."""
        client = self._build_client()

        session_path = client.session_path(
            project=self.project_id,
            location=self.location,
            agent=self.agent_id,
            session=session_id,
        )

        request = session.DetectIntentRequest(
            session=session_path,
            query_input=session.QueryInput(
                text=session.TextInput(text=text),
                language_code=self.language_code,
            ),
        )

        response = client.detect_intent(request=request)
        for msg in response.query_result.response_messages:
            if msg.text and msg.text.text:
                return msg.text.text[0]

        raise ValueError("No response from Dialogflow CX agent.")


def load_configs() -> List[Dict[str, Any]]:
    """Loads configurations for all defined failover routes from environment variables."""
    configs: List[Dict[str, Any]] = []
    for i in [1, 2]:
        project_id = os.getenv(f"DIALOGFLOW_PROJECT_ID_{i}")
        agent_id = os.getenv(f"DIALOGFLOW_AGENT_ID_{i}")

        if project_id and agent_id:
            configs.append({
                "name": f"Cloud {i}",
                "project_id": project_id,
                "agent_id": agent_id,
                "location": os.getenv(f"DIALOGFLOW_LOCATION_{i}", "us-central1"),
                "language_code": os.getenv(f"DIALOGFLOW_LANGUAGE_{i}", "fr"),
                "key_b64": os.getenv(f"GOOGLE_CLOUD_CREDENTIALS_BASE64_{i}"),
            })
    return configs


def query_with_failover(text: str, session_id: str = "default") -> str:
    """Try each configured Dialogflow CX project until one succeeds."""
    configs = load_configs()

    if not configs:
        logger.error("No Dialogflow CX routes configured. Check your .env file.")
        return "Error: Missing configuration."

    for config_dict in configs:
        try:
            route = DialogflowRoute(config_dict)
            result = route.query(text, session_id)
            logger.success(f"[{route.name}] Dialogflow CX response received.")
            return result
        except Exception as e:
            logger.warning(f"[{config_dict.get('name', 'Unknown')}] Failed: {e}")
            continue

    return "All Dialogflow CX routes exhausted."


if __name__ == "__main__":
    logger.info("Dialogflow CX Route Initialized.")
    prompt_test = "Qui est le président de la France actuellement ?"
    logger.info(f"Sending: '{prompt_test}'")

    result = query_with_failover(prompt_test)
    print(f"\n[RESPONSE]: {result}\n")
