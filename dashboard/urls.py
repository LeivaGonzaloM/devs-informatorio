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
    path('dashboard/usuarios', views.blockUser, name='listaUsuarios'),
]
