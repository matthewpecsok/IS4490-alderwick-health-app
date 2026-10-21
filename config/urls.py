from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Alderwick Family Health administration"
admin.site.site_title = "Alderwick admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("portal/", include("portal.urls")),
    path("staff/front-office/", include("frontdesk.urls")),
    path("staff/clinician/", include("clinician.urls")),
    path("staff/ai-operations/", include("aiops.urls")),
    path("dev/", include("devtools.urls")),  # developer tools, only served when DEBUG is on
    path("", include("public.urls")),
]

handler403 = "public.views.permission_denied"
handler404 = "public.views.page_not_found"
