
from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Páginas públicas
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),

    # Apps
    path('articulos/', include('posts.urls')),      # Artículos
    path('informes/', include('informes.urls')),    # Informes
    path('dashboard/', include('dashboard.urls')),  # Dashboard / admin
    path('', include('users.urls')),                # Usuarios públicos y login/registro
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)