# core_config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings               # Importar settings
from django.conf.urls.static import static     # Importar static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ventas/', include('ventas.urls')),
    path('', RedirectView.as_view(url='/ventas/clientes/', permanent=True)),
]

# --- AÑADE ESTA LÍNEA AL FINAL ---
# Esto solo funciona en modo DEBUG (desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)