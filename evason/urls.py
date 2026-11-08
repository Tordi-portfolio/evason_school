from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Evason International Secondary School"
admin.site.site_title = "Evason Admin"
admin.site.index_title = "School administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("", include("accounts.urls")),
    path("portal/", include("academics.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
