from django.conf import settings

PRACTICE = {
    "name": "Alderwick Family Health",
    "main_phone": "(801) 555-0100",
    "billing_phone": "(801) 555-0199",
    "nurse_line": "(801) 555-0190",
}


def practice(request):
    return {"practice": PRACTICE, "debug_banner": settings.DEBUG}
