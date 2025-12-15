from django.urls import path
from posts import views

# app_name = 'posts'

urlpatterns = [
    path('', views.posts, name='posts'),  # /articulos/
    path('crear/', views.createPost, name='crearPost'),
    path('<int:post_id>/', views.postDetail, name='detallePost'),
    path('<int:post_id>/editar/', views.editPost, name='editarPost'),
    path('<int:post_id>/eliminar/', views.deletePost, name='eliminarPost'),

    # Comentarios
    path('comentario/editar/<int:id>/', views.editarCommentAJAX, name='editarCommentAJAX'),
    path('comentario/eliminar/<int:id>/', views.eliminarCommentAJAX, name='eliminarCommentAJAX'),
]
