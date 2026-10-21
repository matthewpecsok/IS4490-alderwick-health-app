import time

from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from clinic import gemini

DEFAULT_PROMPT = "Reply with one short sentence confirming that you received this message."


def gemini_check(request):
    """Developer page for testing the Gemini connection. Not linked from the app; only served when DEBUG is on."""
    if not settings.DEBUG:
        raise Http404

    key = gemini.api_key()
    context = {
        "prompt": DEFAULT_PROMPT,
        "model": gemini.model_name(),
        "backend": "Vertex AI (GCP)" if gemini.uses_vertex_ai() else "Gemini API",
        "key_hint": f"set, ends in ...{key[-4:]}" if key else "",
    }
    if request.method == "POST":
        context["prompt"] = request.POST.get("prompt", "").strip() or DEFAULT_PROMPT
        started = time.monotonic()
        try:
            context["reply"] = gemini.generate_text(context["prompt"])
        except gemini.GeminiError as exc:
            context["error"] = str(exc)
        context["duration_ms"] = round((time.monotonic() - started) * 1000)
    return render(request, "devtools/gemini_check.html", context)
