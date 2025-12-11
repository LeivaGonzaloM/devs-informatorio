from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),

    # Artículos
    path('dashboard/articulos/', views.listaArticulos, name='listaArticulos'),
    path('crearArticulo/', views.crearArticulo, name='crearArticulo'),
    path('editarArticulo/<int:post_id>/', views.editarArticulo, name='editarArticulo'),
    path('dashboard/<int:post_id>/eliminarPost/', views.admdelPost, name='deletePost'),
    path('articulo/toggle/<int:post_id>/', views.toggleOculto, name='toggleOculto'),

    # INFORMES
    path("dashboard/informes/", views.listaInformes, name="listaInformes"),
    path("dashboard/informes/crear/", views.crearInforme, name="createInforme"),
    path("dashboard/informes/editar/<int:inf_id>/", views.editarInforme, name="editInforme"),
    path("dashboard/informes/eliminar/<int:inf_id>/", views.eliminarInforme, name="eliminarInforme"),
    path('informes/ver/<int:pk>/', views.verInforme, name='verInforme'),
    path("dashboard/informes/toggle/<int:inf_id>/", views.toggleOcultoInforme, name="toggleOcultoInforme"),

    # Reports
    path('dashboard/reports/', views.adminReports, name='adminReports'),

    # Usuarios
    path('eliminar-usuario/', views.eliminar_usuario, name='eliminar_usuario'),
    path("usuarios/", views.listUsuarios, name="listaUsuarios"),
    path("usuarios/perfil/<int:user_id>/", views.perfilUsuario, name="perfilUsuario"),
    path('usuarios/<int:user_id>/', views.perfilUsuario, name='perfilUsuario'),
    path('crear-usuario/', views.crearUsuario, name='crearUsuario'),
    path('usuarios/<int:user_id>/editar/', views.editarUsuario, name='editarUsuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminarUsuario, name='eliminarUsuario'),
    path('bloquearUsuario/<int:user_id>/', views.blockUser, name='bloquearUsuario'),
    path('bloquear-usuario/', views.block_Usuario, name='blockUsuario'),
    path('desbloquearUsuario/<int:user_id>/', views.unblockUser, name='desbloquearUsuario'),

    # Advertencias
    path("dashboard/advertencias/", views.lista_advertencias, name="listaAdvertencias"),
    path('advertir-usuario/', views.advertir_usuario, name='advertirUser'),
    path("warn/<int:user_id>/", views.warn_user, name="advertirUsuario"),
    path("dashboard/advertencias/eliminar/<int:adv_id>/", views.eliminar_advertencia, name="eliminarAdvertencia"),
]

