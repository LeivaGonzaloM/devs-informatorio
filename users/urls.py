from django.urls import path
from users import views
from .views import profileView, editProfile
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('registro/', views.signup, name='register'),
    path('logout/', views.signout, name='logout'),
    path('login/', views.signin , name='login'),

    # Perfil
    path('perfil/', profileView, name='profile'),                  # Perfil propio
    path('perfil/<str:username>/', profileView, name='profile-username'),  # Perfil de otro usuario
    path('editar/', editProfile, name='editProfile'),

    # Reportes de usuario
    path('report/user/<int:user_id>/', views.reportUser, name='reportUser'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)