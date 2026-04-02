"""
TRINITY ROUTE: DIALOGFLOW CX
============================
Dialogflow CX integration as a free conversational AI route.
Supports multi-project failover with service account authentication.
"""

import os
import json
import base64
from typing import Dict, List, Optional
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def _build_configs() -> List[Dict]:
    """Build Dialogflow configs from environment variables."""
    configs = []
    for i in [1, 2]:
        project_id = os.getenv(f"DIALOGFLOW_PROJECT_ID_{i}")
        agent_id = os.getenv(f"DIALOGFLOW_AGENT_ID_{i}")
        if project_id and agent_id:
            key_var = "GOOGLE_CLOUD_CREDENTIALS_BASE64" if i == 1 else f"GOOGLE_CLOUD_{i-1}_CREDENTIALS_BASE64"
            configs.append({
                "name": f"Cloud {i}",
                "project_id": project_id,
                "agent_id": agent_id,
                "key_var": key_var,
                "location": os.getenv(f"DIALOGFLOW_LOCATION_{i}", "us-central1"),
            })
    return configs

def _get_credential_json(key_var: str) -> Optional[str]:
    """Extract credential JSON from base64-encoded env var."""
    val = os.getenv(key_var)
    if val:
        return base64.b64decode(val).decode("utf-8")
    return None

def execute_dialogflow(config: Dict, text: str, session_id: str) -> str:
    """Execute Dialogflow CX detect intent."""
    from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
    from google.cloud.dialogflowcx_v3beta1.types import session
    from google.oauth2 import service_account

    key_json = _get_credential_json(config["key_var"])
    if not key_json:
        raise ValueError(f"Credential key missing for {config['name']}")

    creds = service_account.Credentials.from_service_account_info(
        json.loads(key_json)
    )
    client = SessionsClient(
        credentials=creds,
        client_options={
            "api_endpoint": f"{config['location']}-dialogflow.googleapis.com:443"
        },
    )

    session_path = client.session_path(
        project=config["project_id"],
        location=config["location"],
        agent=config["agent_id"],
        session=session_id,
    )

    request = session.DetectIntentRequest(
        session=session_path,
        query_input=session.QueryInput(
            text=session.TextInput(text=text), language_code="fr"
        ),
    )

    response = client.detect_intent(request=request)
    for msg in response.query_result.response_messages:
        if msg.text and msg.text.text:
            return msg.text.text[0]
    return ""

def query_with_failover(text: str, session_id: str = "default") -> str:
    """Try each configured Dialogflow project until one succeeds."""
    configs = _build_configs()
    for config in configs:
        try:
            result = execute_dialogflow(config, text, session_id)
            logger.info(f"[DIALOG] Success via {config['name']}")
            return result
        except Exception as e:
            logger.warning(f"[DIALOG] {config['name']} failed: {e}")
            continue
    return "All Dialogflow routes exhausted."

if __name__ == "__main__":
    print("Dialogflow CX Route loaded.")
    result = query_with_failover("Bonjour, comment vas-tu ?")
    print(f"Response: {result}")
