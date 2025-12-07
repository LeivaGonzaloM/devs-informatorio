from django.urls import path
from posts import views

# app_name = 'posts'

urlpatterns = [
    path('articulos/', views.posts, name='posts'),
    path('articulos/crear', views.createPost, name='crearPost'),
    path('articulos/<int:post_id>/', views.postDetail, name='detallePost'),
    path('articulos/<int:post_id>/eliminar', views.deletePost, name='eliminarPost'),
    path('articulos/editar/<int:post_id>', views.editPost, name='editarPost'),
    # urls.py
    path('comentario/editar/<int:id>/', views.editarCommentAJAX, name='editarCommentAJAX'),
    path('comentario/eliminar/<int:id>/', views.eliminarCommentAJAX, name='eliminarCommentAJAX'),
]
