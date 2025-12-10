from django.urls import path
from posts import views as post_views
from informes import views as informe_views
from .uploads import ckeditor5_upload


# app_name = 'posts'

urlpatterns = [
    path('informes/crear', informe_views.crear_informe, name='crearInforme'),
    path('ckeditor5/upload/', ckeditor5_upload, name='ckeditor5_upload'),
    path('detalle/<int:pk>/', informe_views.detalleInforme, name='detalleInforme'),
    path('editar/<int:pk>/', informe_views.editarInforme, name='editarInforme'),
    path('eliminar/<int:pk>/', informe_views.eliminarInforme, name='eliminarInforme'),

    # Comentarios (editar/eliminar vía fetch desde JS)
    path('comentario/editar/<int:pk>/', informe_views.editarComentarioInforme, name='editarComentarioInforme'),
    path('comentario/eliminar/<int:pk>/', informe_views.eliminarComentarioInforme, name='eliminarComentarioInforme'),
    path('', informe_views.informes, name='informes'),
]

