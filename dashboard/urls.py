from django.urls import path
from . import views

# app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<int:post_id>/eliminarPost', views.admdelPost, name='deletePost'),
    path('delete-user/<int:user_id>/', views.deleteUser, name='deleteUser'),
    path('dashboard/reports', views.adminReports, name='adminReports'),
    path('bloquearUsuario/<int:user_id>/', views.blockUser, name='bloquearUsuario'),
    path('desbloquearUsuario/<int:user_id>/', views.unblockUser, name='desbloquearUsuario'),
    path("usuarios/", views.listUsuarios, name="listaUsuarios"),
    path("usuarios/perfil/<int:user_id>/", views.perfilUsuario, name="perfilUsuario"),
    path('usuarios/', views.listUsuarios, name='listUsuarios'),
    path('usuarios/<int:user_id>/', views.perfilUsuario, name='perfilUsuario'),
    path('crear-usuario/', views.crearUsuario, name='crearUsuario'),
    path('usuarios/<int:user_id>/editar/', views.editarUsuario, name='editarUsuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminarUsuario, name='eliminarUsuario'),
    path("dashboard/advertencias/", views.lista_advertencias, name="listaAdvertencias"),
    path("warn/<int:user_id>/", views.warn_user, name="advertirUsuario"),
    path("dashboard/advertencias/eliminar/<int:adv_id>/", views.eliminar_advertencia, name="eliminarAdvertencia"),
    path('crearArticulo/', views.crearArticulo, name='crearArticulo'), 
]
