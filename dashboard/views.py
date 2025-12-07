from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.models import User
from users.models import Profile
from django.http import HttpResponseForbidden, HttpResponse
from users.models import UserReport

# Create your views here.
@login_required
def dashboard(request):

    if request.user.is_staff or request.user.is_superuser:

        current_admin = request.user
        profile, created = Profile.objects.get_or_create(user=current_admin)

        users = User.objects.all()
        profiles = Profile.objects.all()
        posts = Post.objects.all()

        return render(request, 'dashboard/baseAdmin.html', {
            'admin_profile': profile,
            'current_admin': current_admin,
            'users': users,
            'profiles': profiles,
            'posts': posts,
        })

    else:
        return render(request, 'dashboard/acceso_denegado.html')

    

@login_required
def deleteUser(request, user_id):
    # Solo administradores pueden eliminar usuarios
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("No tenés permiso para realizar esta acción.")

    user_to_delete = get_object_or_404(User, pk=user_id)

    # Prevenir que un admin se elimine a sí mismo
    if user_to_delete == request.user:
        return HttpResponseForbidden("No podés eliminar tu propio usuario.")

    if request.method == "POST":
        user_to_delete.delete()
        return redirect('dashboard')

    # Si acceden por GET, confirmación opcional
    return redirect('dashboard')


@login_required
def admdelPost(request, post_id):
      post = get_object_or_404(Post, pk=post_id)
      # Permite borrar si es admin (staff o superuser) o si es el dueño
      if request.user.is_staff or request.user.is_superuser or post.user == request.user:
            post.delete()
            return redirect('dashboard')
      

@login_required
def adminReports(request):
    current_admin = request.user
    profile, created = Profile.objects.get_or_create(user=current_admin)
    if not request.user.is_superuser:
        return HttpResponse("No autorizado")

    reports = UserReport.objects.all().order_by('-created')
    return render(request, 'dashboard/adminReports.html', {
        'admin_profile': profile,
        'reports': reports,
    })

@login_required
def blockUser(request, user_id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    if not request.user.is_staff:
        return HttpResponseForbidden("No tenés permisos.")

    user_to_block = get_object_or_404(User, pk=user_id)
    profile = user_to_block.profile

    if request.method == "POST":
        minutes = int(request.POST.get("minutes", 0))
        hours   = int(request.POST.get("hours", 0))
        days    = int(request.POST.get("days", 0))

        profile.block(minutes=minutes, hours=hours, days=days)
        return redirect("dashboard")

    return render(request, "dashboard/usuarios/bloquearUsuario.html", {
        'admin_profile': profileAdmin,
        "user": user_to_block
    })

def listUser(request):
    return render(request, 'dashboard/usuarios/listaUsuarios.html')

@login_required
def unblockUser(request, user_id):
    # Solo staff puede desbloquear
    if not request.user.is_staff:
        return HttpResponseForbidden("No tenés permisos.")

    # Aceptamos solo POST por seguridad
    if request.method != "POST":
        return redirect('dashboard')  # o la vista de lista de usuarios

    user_to_unblock = get_object_or_404(User, pk=user_id)
    profile = user_to_unblock.profile

    # Si tenés métodos en Profile, usalos; sino lo hacemos directamente:
    profile.blocked_until = None
    # si usás un flag booleano:
    try:
        profile.is_blocked = False
    except Exception:
        pass

    profile.save()

    return redirect('dashboard')  # o 'dashboardUsuarios' según tu nombre de ruta