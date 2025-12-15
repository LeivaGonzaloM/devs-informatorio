from django.urls import path
from . import views
from core.views import contacto

urlpatterns = [

    # ======================================================
    # Dashboard principal
    # ======================================================
    path('', views.dashboard, name='dashboard'),

    # ======================================================
    # ARTÍCULOS
    # ======================================================
    path('articulos/', views.listaArticulos, name='listaArticulos'),
    path('articulos/crear/', views.crearArticulo, name='crearArticulo'),
    path('articulos/<int:post_id>/editar/', views.editarArticulo, name='editarArticulo'),
    path('articulos/<int:post_id>/eliminar/', views.admdelPost, name='deletePost'),
    path('articulos/toggle/<int:post_id>/', views.toggleOculto, name='toggleOculto'),

    # ======================================================
    # INFORMES
    # ======================================================
    path('informes/', views.listaInformes, name='listaInformes'),
    path('informes/crear/', views.crearInforme, name='createInforme'),
    path('informes/ver/<int:pk>/', views.verInforme, name='verInforme'),
    path('informes/editar/<int:inf_id>/', views.editarInforme, name='editInforme'),
    path('informes/eliminar/<int:inf_id>/', views.eliminarInforme, name='deleteInforme'),
    path('informes/toggle/<int:inf_id>/', views.toggleOcultoInforme, name='toggleOcultoInforme'),

    # ======================================================
    # USUARIOS
    # ======================================================
    path('usuarios/', views.listUsuarios, name='listaUsuarios'),
    path('usuarios/crear/', views.crearUsuario, name='crearUsuario'),
    path('usuarios/<int:user_id>/', views.perfilUsuario, name='perfilUsuario'),
    path('usuarios/<int:user_id>/editar/', views.editarUsuario, name='editarUsuario'),
    path('eliminarUsuario/', views.dashEliminarUsuario, name='dashEliminarUsuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminarUsuario, name='eliminarUsuario'),

    # ======================================================
    # BLOQUEOS (UNA SOLA LÓGICA)
    # ======================================================
    # Formulario con select (atajo)
    path('usuarios/bloquear/', views.dashBlockUsuario, name='dashBlockUsuario'),

    # Bloqueo usuarios
    path(
        "usuarios/bloquear/<int:user_id>/",
        views.blockUserForm,
        name="blockUserForm"
    ),
    path(
        "usuarios/bloquear/confirmar/",
        views.blockUserConfirm,
        name="blockUserConfirm"
    ),
    path(
        "usuarios/desbloquear/<int:user_id>/",
        views.unblockUser,
        name="unblockUser"
    ),

    # Lista de bloqueados
    path('usuarios/bloqueados/', views.listaBloqueados, name='listaBloqueados'),

    # ======================================================
    # ADVERTENCIAS
    # ======================================================
    path('advertencias/', views.lista_advertencias, name='listaAdvertencias'),
    path('advertencias/crear/<int:user_id>/', views.warn_user, name='advertirUsuario'),
    path('advertirUsuario/', views.dashAdvertirUsuario, name='dashAdvertirUsuario'),
    path('advertencias/eliminar/<int:adv_id>/', views.eliminar_advertencia, name='eliminarAdvertencia'),

    # ======================================================
    # REPORTES
    # ======================================================
    path('reports/', views.dashReportsUsers, name='dashReportsUsers'),

    # ======================================================
    # PERFIL ADMIN
    # ======================================================
    path('perfil-admin/', views.perfil_admin, name='perfilAdmin'),
    path('perfil-admin/editar/<int:user_id>/', views.editar_perfil_admin, name='editarPerfilAdmin'),

    # ======================================================
    # ATAJOS DE ADMINISTRACIÓN
    # ======================================================
    path('administrar/usuarios/', views.administrar_usuarios, name='administrarUsuarios'),
    path('administrar/articulos/', views.administrar_articulos, name='administrarArticulos'),
    path('administrar/informes/', views.administrar_informes, name='administrarInformes'),

    # ======================================================
    # MENSAJES DE CONTACTO
    # ======================================================
    path('mensajes/', views.mensajes_admin, name='mensajesAdmin'),
    path('mensajes/<int:id>/', views.ver_mensaje, name='verMensaje'),
    path('mensajes/<int:id>/eliminar/', views.eliminar_mensaje, name='eliminarMensaje'),
]

