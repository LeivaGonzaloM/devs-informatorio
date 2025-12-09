from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.models import User
from users.models import Profile
from django.http import HttpResponseForbidden, HttpResponse
from users.models import UserReport
from django.contrib.auth.decorators import user_passes_test
from users.forms import WarningForm
from users.models import Warning
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from django import forms
from .forms import EditUserForm, EditProfileForm, AdminPasswordChangeForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from posts.models import Post
from posts.forms import PostForm
from users.forms import ProfileUpdateForm
from .forms import CustomUserCreationForm


# Create your views here.
@login_required
def dashboard(request):

    if request.user.is_staff or request.user.is_superuser:

        current_admin = request.user
        profile, created = Profile.objects.get_or_create(user=current_admin)

        users = User.objects.all()
        profiles = Profile.objects.all()
        posts = Post.objects.all()
        reports = UserReport.objects.all().order_by('-created')  # últimos primero
        warnings = Warning.objects.all()
        # Contar usuarios actualmente bloqueados
        blocked_count = sum(1 for p in profiles if p.is_currently_blocked)
        # Limitar los reportes que se muestran (ej: 5 más recientes)
        recent_reports = reports[:5]

        return render(request, 'dashboard/dashboardIndex.html', {
            'admin_profile': profile,
            'current_admin': current_admin,
            'users': users,
            'profiles': profiles,
            'reports':reports,
            'warnings':warnings,
            "blocked_count": blocked_count,
            "recent_reports": recent_reports,
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
        minutes = int(request.POST.get("minutes") or 0)
        hours   = int(request.POST.get("hours") or 0)
        days    = int(request.POST.get("days") or 0)

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

# Sistema de advertencia a usuarios
@user_passes_test(lambda u: u.is_superuser)
def warn_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    current_admin = request.user
    profile, created = Profile.objects.get_or_create(user=current_admin)

    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        nivel = request.POST.get("nivel")
        duracion = request.POST.get("duracion")  # <-- NUEVO

        if mensaje and nivel and duracion:

            # calcular expiración
            expires_at = None

            if duracion == "24h":
                expires_at = now() + timedelta(hours=24)
            elif duracion == "3d":
                expires_at = now() + timedelta(days=3)
            elif duracion == "1w":
                expires_at = now() + timedelta(weeks=1)
            elif duracion == "1m":
                expires_at = now() + timedelta(days=30)
            elif duracion == "perm":
                expires_at = None  # permanente

            # crear advertencia
            Warning.objects.create(
                user=user,
                admin=request.user,
                mensaje=mensaje,
                nivel=nivel,
                expires_at=expires_at,
                active=True
            )

            return redirect("listaAdvertencias")

    return render(request, "dashboard/usuarios/advertirUsuario.html", {
        "admin_profile": profile,
        "usuario": user
    })


@user_passes_test(lambda u: u.is_superuser)
def lista_advertencias(request):
    current_admin = request.user
    profile, created = Profile.objects.get_or_create(user=current_admin)

    # Solo superusuarios pueden entrar
    if not current_admin.is_superuser:
        return HttpResponse("No autorizado")

    advertencias = Warning.objects.all().order_by("-created_at")

    # Actualizamos activas/expiradas según la fecha
    for adv in advertencias:
        adv.check_active()

    return render(request, "dashboard/usuarios/listaAdvertencias.html", {
        "admin_profile": profile,
        "advertencias": advertencias
    })

@user_passes_test(lambda u: u.is_superuser)
def eliminar_advertencia(request, adv_id):
    advertencia = get_object_or_404(Warning, id=adv_id)

    if request.method == "POST":
        advertencia.delete()
        return redirect("listaAdvertencias")

    return HttpResponse("Método no permitido", status=405)


# Lista usuarios
def listUsuarios(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    query = request.GET.get("q", "")

    # obtener todos los perfiles con el user relacionado
    profiles = Profile.objects.select_related("user").all().order_by("user__username")

    # FILTRO DE BÚSQUEDA
    if query:
        profiles = profiles.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(full_name__icontains=query)
        )

    context = {
        "admin_profile": profileAdmin,
        "profiles": profiles,
        "query": query
    }

    return render(request, "dashboard/usuarios/listaUsuarios.html", context)

# def perfilUsuario(request, user_id):
#     current_admin = request.user
#     profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
#     user = get_object_or_404(User, id=user_id)
#     profile = Profile.objects.get(user=user)

#     return render(request, "dashboard/usuarios/userProfile/perfilUsuario.html", {
#         "admin_profile": profileAdmin,
#         "user_obj": user,
#         "profile": profile
#     })
# --------------------------------------------------------------
# PERFIL DEL USUARIO
# --------------------------------------------------------------
def perfilUsuario(request, user_id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    return render(request, "dashboard/usuarios/userProfile/perfilUsuario.html", {
        "admin_profile": profileAdmin,
        "u": user,
        "profile": profile
    })

# --------------------------------------------------------------
# EDITAR USUARIO + PROFILE
# --------------------------------------------------------------
def editarUsuario(request, user_id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    u = get_object_or_404(User, id=user_id)
    profile = u.profile

    if request.method == "POST":
        u_form = EditUserForm(request.POST, instance=u)
        p_form = EditProfileForm(request.POST, request.FILES, instance=profile)

        new_password = request.POST.get("password")

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            # Cambiar la contraseña si se escribió algo
            if new_password:
                u.set_password(new_password)
                u.save()
                messages.success(request, "Usuario y contraseña actualizados correctamente.")
            else:
                messages.success(request, "Usuario actualizado correctamente.")

            return redirect("perfilUsuario", user_id=u.id)
    else:
        u_form = EditUserForm(instance=u)
        p_form = EditProfileForm(instance=profile)

    return render(request, "dashboard/usuarios/userProfile/editarUsuario.html", {
        "u_form": u_form,
        "p_form": p_form,
        "admin_profile": profileAdmin,
        "u": u
    })

# --------------------------------------------------------------
# ELIMINAR USUARIO + PROFILE
# --------------------------------------------------------------
@staff_member_required  # Solo administradores pueden eliminar
def eliminarUsuario(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"Usuario '{username}' eliminado correctamente.")
        return redirect("listUsuarios")  # Ajusta al nombre de tu lista de usuarios

    return render(request, "dashboard/usuarios/userProfile/eliminarUsuario.html", {
        "u": user_obj
    })

# --------------------------------------------------------------
# CREAR USER + PROFILE
# --------------------------------------------------------------
# Solo administradores
@user_passes_test(lambda u: u.is_staff)
def crearUsuario(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    if request.method == 'POST':
        # Campos manuales del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Formulario del profile
        p_form = ProfileUpdateForm(request.POST, request.FILES)

        # Validaciones
        if not username or not email or not password or not password2:
            messages.error(request, "Completá todos los campos obligatorios.")
        elif password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
        else:
            # Crear usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Guardar profile
            if p_form.is_valid():
                profile, created = Profile.objects.get_or_create(user=user)
                profile.full_name = p_form.cleaned_data['full_name']
                profile.phone = p_form.cleaned_data['phone']
                profile.bio = p_form.cleaned_data['bio']
                if request.FILES.get('avatar'):
                    profile.avatar = request.FILES['avatar']
                profile.save()

            else:
                # Si hay error en profile, borramos el user creado
                user.delete()
                messages.error(request, "Error en los datos del perfil.")
                return redirect('crearUsuario')

            messages.success(request, f'Usuario {user.username} creado con éxito.')
            return redirect('dashboard')
    else:
        p_form = ProfileUpdateForm()

    context = {
        "admin_profile": profileAdmin,
        "p_form": p_form
    }
    return render(request, 'dashboard/usuarios/crearUsuario.html', context)


# --------------------------------------------------------------
# CREAR POST 
# --------------------------------------------------------------
def crearArticulo(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, f'Artículo "{post.title}" creado con éxito.')
            return redirect('dashboard')
    else:
        form = PostForm()

    context = {
        "admin_profile": profileAdmin,
        'form': form
    }
    return render(request, 'dashboard/articulos/crearArticulo.html', context)

# --------------------------------------------------------------
# EDITAR POST 
# --------------------------------------------------------------
@login_required
def editarArticulo(request, post_id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    post = get_object_or_404(Post, id=post_id)

    # Solo el dueño o staff puede editar
    if not request.user.is_staff and post.user != request.user:
        messages.error(request, "No tenés permiso para editar este artículo.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.edited_by = request.user
            edited_post.last_edited = now()
            edited_post.save()
            messages.success(request, f'Artículo "{edited_post.title}" actualizado con éxito.')
            return redirect('dashboard')
    else:
        form = PostForm(instance=post)

    context = {
        "admin_profile": profileAdmin,
        "form": form,
        "post": post,
    }
    return render(request, 'dashboard/articulos/editarArticulo.html', context)
