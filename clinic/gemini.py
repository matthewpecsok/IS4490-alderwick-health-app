"""The one place the application talks to Google's Gemini models.

Configuration comes from environment variables. In GitHub Codespaces, add them
as Codespaces secrets (GitHub > Settings > Codespaces > Secrets) and they are
set automatically in every Codespace for this repository:

    GEMINI_API_KEY             API key from your GCP project or Google AI Studio (required)
    GEMINI_MODEL               model ID to use (optional, defaults to DEFAULT_MODEL)
    GOOGLE_GENAI_USE_VERTEXAI  "true" sends requests to Vertex AI (aiplatform.googleapis.com),
                               which is what GCP project keys need; the Codespace sets this.
                               Unset or "false" sends them to the AI Studio endpoint
                               (generativelanguage.googleapis.com), for AI Studio keys.

Example, from any view or service:

    from clinic import gemini

    try:
        summary = gemini.generate_text(
            f"Summarize this policy for a patient in two sentences:\\n\\n{policy.body}",
            system_instruction="You are a helpful assistant for Alderwick Family Health.",
        )
    except gemini.GeminiError as exc:
        summary = None  # show a friendly message instead of crashing the page

Prompts and replies are never written to the logs, only the model name and timing.
"""

import logging
import os
import time

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.5-flash-lite"

logger = logging.getLogger("alderwick.ai")


class GeminiError(Exception):
    """Gemini is not configured or the request failed."""


def api_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


def model_name():
    return os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL


def uses_vertex_ai():
    return os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true")


def get_client():
    key = api_key()
    if not key:
        raise GeminiError(
            "GEMINI_API_KEY is not set. Add it as a GitHub Codespaces secret, then rebuild or restart the Codespace."
        )
    return genai.Client(api_key=key, vertexai=uses_vertex_ai())


def generate_text(prompt, *, system_instruction=None, model=None):
    """Send a text prompt to Gemini and return the reply as a string."""
    model = model or model_name()
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    client = get_client()
    started = time.monotonic()
    try:
        response = client.models.generate_content(model=model, contents=prompt, config=config)
    except Exception as exc:
        logger.warning(
            "gemini_failed model=%s duration_ms=%.1f error=%s",
            model,
            (time.monotonic() - started) * 1000,
            type(exc).__name__,
        )
        message = f"{type(exc).__name__}: {exc}"
        if "API_KEY_SERVICE_BLOCKED" in message:
            message = (
                "This key is not allowed to call the endpoint the request went to. GCP keys need "
                "GOOGLE_GENAI_USE_VERTEXAI=true; AI Studio keys need it unset.\n\n" + message
            )
        raise GeminiError(message) from exc
    logger.info("gemini_call model=%s duration_ms=%.1f", model, (time.monotonic() - started) * 1000)
    return response.text or ""
