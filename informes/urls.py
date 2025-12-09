from django.urls import path
from posts import views
from informes import views

# app_name = 'posts'

urlpatterns = [
    path('informes/', views.informes, name='informes'),
    path('informes/crear', views.crear_informe, name='crearInforme'),
    path('detalle/<int:pk>/', views.detalleInforme, name='detalleInforme'),
    path('editar/<int:pk>/', views.editarInforme, name='editarInforme'),
    path('eliminar/<int:id>/', views.eliminarInforme, name='eliminarInforme'),

    # Comentarios (editar/eliminar vía fetch desde JS)
    path('comentario/editar/<int:pk>/', views.editarComentarioInforme, name='editarComentarioInforme'),
    path('comentario/eliminar/<int:pk>/', views.eliminarComentarioInforme, name='eliminarComentarioInforme'),
]
