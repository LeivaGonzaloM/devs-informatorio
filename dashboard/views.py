from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Post
from django.contrib.auth.models import User
from users.models import Profile
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from users.models import UserReport
from django.contrib.auth.decorators import user_passes_test
from users.forms import WarningForm
from users.models import Warning
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from django import forms
from .forms import EditUserForm, EditProfileForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from posts.models import Post
from posts.forms import PostForm
from users.forms import ProfileUpdateForm
from informes.models import Informe
from informes.forms import InformeForm
from django.db.models import Count
from django.utils import timezone
from dashboard.models import MensajeContacto
from django.urls import reverse


# Create your views here.
@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        current_admin = request.user
        profile, created = Profile.objects.get_or_create(user=current_admin)

        # Datos principales
        users = User.objects.all()
        profiles = Profile.objects.select_related('user').all()
        posts = Post.objects.all()
        informes = Informe.objects.all().order_by("-created")
        reports = UserReport.objects.all().order_by('-created')
        warnings = Warning.objects.all()

        # Contadores y métricas
        blocked_count = sum(1 for p in profiles if getattr(p, 'is_currently_blocked', False))
        active_users = sum(1 for p in profiles if getattr(p, 'is_currently_blocked', False) is False)
        warned_users = warnings.count()
        reported_users = reports.values('reported_user').distinct().count()
        total_posts = posts.count()
        visible_posts = posts.filter(oculto=False).count()
        hidden_posts = posts.filter(oculto=True).count()
        total_informes = informes.count()
        visible_informes = informes.filter(oculto=False).count()
        hidden_informes = informes.filter(oculto=True).count()
        total_reports = reports.count()

        # Listas recientes
        recent_signups = users.order_by('-date_joined')[:5]
        recent_posts = posts.order_by('-created')[:5]
        recent_reports = reports[:5]

        # Últimos usuarios reportados
        latest_reported_users = User.objects.filter(
            id__in=reports.values_list('reported_user', flat=True)
        ).order_by('-date_joined')[:5]  # Limitamos a 5 recientes

        # Últimos usuarios bloqueados
        latest_blocked_users = profiles.filter(
            is_blocked=True
        ).order_by('-blocked_until')[:5]

        # Más comentados
        most_commented_posts = posts.annotate(comment_count=Count('comments')).order_by('-comment_count')[:5]

        # Autores más activos
        top_authors = posts.values('user__username').annotate(total_posts=Count('user')).order_by('-total_posts')[:5]

        # Usuarios advertidos (se reemplaza la sección de "Reportes por tipo")
        warned_users_list = User.objects.filter(
            id__in=warnings.values_list('user', flat=True)
        ).order_by('-date_joined')[:5]

        context = {
            'current_admin': current_admin,
            'admin_profile': profile,
            'users': users,
            'profiles': profiles,
            'posts': posts,
            'informes': informes,
            'reports': reports,
            'warnings': warnings,
            'blocked_count': blocked_count,
            'active_users': active_users,
            'warned_users': warned_users,
            'reported_users': reported_users,
            'total_posts': total_posts,
            'visible_posts': visible_posts,
            'hidden_posts': hidden_posts,
            'total_informes': total_informes,
            'visible_informes': visible_informes,
            'hidden_informes': hidden_informes,
            'total_reports': total_reports,
            'recent_signups': recent_signups,
            'recent_posts': recent_posts,
            'recent_reports': recent_reports,
            'latest_reported_users': latest_reported_users,
            'latest_blocked_users': latest_blocked_users,
            'most_commented_posts': most_commented_posts,
            'top_authors': top_authors,
            'warned_users_list': warned_users_list,
        }

        return render(request, 'dashboard/dashboardIndex.html', context)

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
def dashReportsUsers(request):
    current_admin = request.user
    profile, created = Profile.objects.get_or_create(user=current_admin)
    if not request.user.is_superuser:
        return HttpResponse("No autorizado")

    reports = UserReport.objects.all().order_by('-created')
    # 👁 marcar como vistos
    UserReport.objects.filter(visto_admin=False).update(visto_admin=True)
    return render(request, 'dashboard/adminReports.html', {
        'admin_profile': profile,
        'reports': reports,
    })

@login_required
@staff_member_required
def blockUserConfirm(request):
    if request.method != "POST":
        return redirect("dashboard")

    user_id = request.POST.get("user_id")
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    # ============================
    # CASO 1 → blockUserNow.html
    # ============================
    time_unit = request.POST.get("time_unit")
    time_value = request.POST.get("time_value")

    delta = None

    if time_unit and time_value:
        time_value = int(time_value)

        delta_map = {
            "minutes": timedelta(minutes=time_value),
            "hours": timedelta(hours=time_value),
            "days": timedelta(days=time_value),
        }

        delta = delta_map.get(time_unit)

    # ============================
    # CASO 2 → bloquearUsuario.html
    # ============================
    else:
        minutes = int(request.POST.get("minutes", 0))
        hours   = int(request.POST.get("hours", 0))
        days    = int(request.POST.get("days", 0))

        delta = timedelta(
            minutes=minutes,
            hours=hours,
            days=days
        )

        if delta.total_seconds() == 0:
            delta = None  # bloqueo permanente

    # ============================
    # APLICAR BLOQUEO
    # ============================
    profile.is_blocked = True
    profile.blocked_until = now() + delta if delta else None
    profile.save()

    messages.success(
        request,
        f"El usuario {user.username} fue bloqueado correctamente."
    )

    return redirect(request.POST.get("next", "/dashboard/"))



@login_required
@staff_member_required
def dashBlockUsuario(request):
    current_admin = request.user
    profileAdmin, _ = Profile.objects.get_or_create(user=current_admin)
    users = User.objects.all().order_by("username")

    # ==========================
    # POST → bloquear usuario
    # ==========================
    if request.method == "POST":
        user_id = request.POST.get("user")
        time_unit = request.POST.get("time_unit")
        time_value = request.POST.get("time_value")

        if not user_id or not time_value:
            messages.error(request, "Debes seleccionar un usuario y un tiempo.")
            return redirect("dashBlockUsuario")

        # reenviamos al confirmador central
        return redirect(
            reverse("blockUserConfirm") +
            f"?user_id={user_id}&unit={time_unit}&value={time_value}"
        )

    # ==========================
    # GET → mostrar formulario
    # ==========================
    return render(
        request,
        "dashboard/atajos/blockUserNow.html",
        {
            "admin_profile": profileAdmin,
            "users": users,
        },
    )

@login_required
@staff_member_required
def blockUserForm(request, user_id):
    user = get_object_or_404(User, id=user_id)
    current_admin = request.user
    profileAdmin, _ = Profile.objects.get_or_create(user=current_admin)

    return render(
        request,
        "dashboard/usuarios/bloquearUsuario.html",
        {
            "admin_profile": profileAdmin,
            "user": user,
        }
    )

@login_required
@staff_member_required
def unblockUser(request, user_id):
    if request.method != "POST":
        return redirect("dashboard")

    profile = get_object_or_404(Profile, user__id=user_id)
    profile.unblock()

    messages.success(request, f"El usuario {profile.user.username} fue desbloqueado.")

    return redirect(request.POST.get("next", "/dashboard/"))



# Sistema de advertencia a usuarios
@user_passes_test(lambda u: u.is_superuser)
def warn_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    current_admin = request.user
    profile, created = Profile.objects.get_or_create(user=current_admin)

    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        nivel = request.POST.get("nivel")
        duracion = request.POST.get("duracion") 

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

# --------------------------------------------------------------
# PERFIL DEL USUARIO
# --------------------------------------------------------------
def perfilUsuario(request, user_id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=request.user)
    # Si el admin está intentando ver su propio perfil, redirigir a perfilAdmin
    if current_admin.id == user_id:
        return redirect('perfilAdmin')  # Redirige a la vista 'perfilAdmin'

    warnings = Warning.objects.all()
    user = get_object_or_404(User, id=user_id)
    reports = UserReport.objects.filter(reported_user=user)
    profile = user.profile
    return render(request, "dashboard/usuarios/userProfile/perfilUsuario.html", {
        "warnings" : warnings,
        "admin_profile": profileAdmin,
        "u": user,
        "profile": profile,
        "reports" : reports,
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
        return redirect("listaUsuarios")  

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

def listaArticulos(request):
    query = request.GET.get("q", "").strip()
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    posts = Post.objects.all().order_by("-id")

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(user__username__icontains=query)
        )

    context = {
        "admin_profile": profileAdmin,
        "posts": posts,
        "query": query,
    }
    return render(request, "dashboard/articulos/listaArticulos.html", context)

@user_passes_test(lambda u: u.is_superuser)
def toggleOculto(request, post_id):
    if request.method != "POST":
        # opcional: devolver 405 o redirigir
        return redirect("dashboard")

    post = get_object_or_404(Post, id=post_id)
    post.oculto = not post.oculto
    post.save()

    if post.oculto:
        messages.success(request, f'El artículo "{post.title}" quedó oculto.')
    else:
        messages.success(request, f'El artículo "{post.title}" se publicó (visible).')

    return redirect("dashboard")

# --------------------------------------------------------------
# Lista de informes 
# --------------------------------------------------------------
@user_passes_test(lambda u: u.is_superuser)
def listaInformes(request):
    query = request.GET.get("q", "")
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    informes = Informe.objects.all().order_by("-created")

    if query:
        informes = informes.filter(
            Q(title__icontains=query) |
            Q(user__username__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, "dashboard/informes/listaInformes.html", {
        "admin_profile" : profileAdmin,
        "informes": informes,
        "query": query,
    })

# --------------------------------------------------------------
# Crear  informes 
# --------------------------------------------------------------
@login_required
def crearInforme(request):
    current_admin = request.user
    profileAdmin, _ = Profile.objects.get_or_create(user=current_admin)

    if request.method == "POST":
        form = InformeForm(request.POST)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.user = request.user
            informe.save()
            messages.success(request, "Informe creado correctamente.")
            return redirect("listaInformes")

    form = InformeForm()
    return render(request, "dashboard/informes/crearInforme.html", {
        "form": form,
        "admin_profile": profileAdmin
    })

# --------------------------------------------------------------
# Editar  informes 
# --------------------------------------------------------------
@login_required
def editarInforme(request, inf_id):
    informe = get_object_or_404(Informe, id=inf_id)
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    if not request.user.is_staff and informe.user != request.user:
        messages.error(request, "No tenés permiso.")
        return redirect("listaInformes")

    if request.method == "POST":
        form = InformeForm(request.POST, instance=informe)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.edited_by = request.user
            edit.save()
            messages.success(request, "Informe actualizado.")
            return redirect("listaInformes")

    else:
        form = InformeForm(instance=informe)

    return render(request, "dashboard/informes/editarInforme.html", {
        "admin_profile": profileAdmin,
        "form": form,
        "informe": informe
    })
# --------------------------------------------------------------
# Eliminar  informes 
# --------------------------------------------------------------
@login_required
def eliminarInforme(request, inf_id):
    informe = get_object_or_404(Informe, id=inf_id)

    if request.method == "POST":
        informe.delete()
        messages.success(request, "Informe eliminado.")
        return redirect("listaInformes")

    return redirect("listaInformes")

# --------------------------------------------------------------
# ocultar  informes 
# --------------------------------------------------------------
@login_required
def toggleOcultoInforme(request, inf_id):
    informe = get_object_or_404(Informe, id=inf_id)

    if request.method != "POST":
        return redirect("listaInformes")

    informe.oculto = not informe.oculto
    informe.save()

    if informe.oculto:
        messages.warning(request, f'Informe "{informe.title}" ocultado.')
    else:
        messages.success(request, f'Informe "{informe.title}" ahora es visible.')

    return redirect("listaInformes")

# --------------------------------------------------------------
# Ver  informe Detalle
# --------------------------------------------------------------
def verInforme(request, pk):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    """
    Vista para mostrar un informe completo desde el dashboard.
    """
    informe = get_object_or_404(Informe, pk=pk)
    
    return render(request, 'dashboard/informes/detalleInforme.html', {
        'admin_profile': profileAdmin,
        'informe': informe,
    })


def dashAdvertirUsuario(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    if request.method == 'POST':
        usuario_id = request.POST['usuario']
        mensaje = request.POST['mensaje']
        nivel = request.POST['nivel']
        duracion = request.POST['duracion']

        usuario = User.objects.get(id=usuario_id)

        # Lógica para crear la advertencia
        warning = Warning(
            user=usuario,
            admin=request.user,
            mensaje=mensaje,
            nivel=nivel,
        )

        # Determina la duración de la advertencia
        if duracion == "24h":
            warning.expires_at = timezone.now() + timedelta(hours=24)
        elif duracion == "3d":
            warning.expires_at = timezone.now() + timedelta(days=3)
        elif duracion == "1w":
            warning.expires_at = timezone.now() + timedelta(weeks=1)
        elif duracion == "1m":
            warning.expires_at = timezone.now() + timedelta(weeks=4)
        elif duracion == "perm":
            warning.expires_at = None  # Permanente

        warning.save()

        return HttpResponseRedirect('/dashboard/')
    
    return render(request, 'dashboard/atajos/advertirUsuarioNow.html', {
        "admin_profile": profileAdmin,
        'usuarios': usuarios})
# Vista para eliminar un usuario
def dashEliminarUsuario(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios disponibles
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')  # Obtener el usuario seleccionado

        if usuario_id:
            usuario = get_object_or_404(User, id=usuario_id)  # Obtener el usuario por ID
            try:
                # Eliminar el usuario seleccionado
                usuario.delete()
                messages.success(request, f"El usuario {usuario.username} ha sido eliminado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al eliminar el usuario: {str(e)}")
            return redirect('dashboard')  # Redirigir al dashboard después de eliminar

    return render(request, 'dashboard/atajos/eliminarUsuarioNow.html', {
        "admin_profile": profileAdmin,
        'usuarios': usuarios})

# --------------------------------------------------------------
# listaBloqueados
# --------------------------------------------------------------

def listaBloqueados(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    # Obtener todos los usuarios bloqueados
    blocked_users = Profile.objects.filter(is_blocked=True)
    return render(request, 'dashboard/usuarios/listaBloqueados.html', {
        "admin_profile": profileAdmin,
        'blocked_users': blocked_users,
        })



# --------------------------------------------------------------
# PERFIL ADMIN
# --------------------------------------------------------------
# Vista para el perfil del administrador
@login_required
def perfil_admin(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    u = request.user
    profile = u.profile  # Asumiendo que tienes una relación OneToOne con Profile

    # Obtener estadísticas (Ejemplo: reportes recibidos, advertencias emitidas)
    # user_reports = u.reports.all()  # Asumiendo que tienes una relación ManyToMany con Report
    # user_warnings = u.warnings.all()  # Asumiendo que tienes una relación ManyToMany con Warnings

    return render(request, 'dashboard/usuarios/userProfile/perfilAdmin.html', {
        'u': u,
        'profile': profile,
        "admin_profile": profileAdmin,
        # 'user_reports': user_reports,
        # 'user_warnings': user_warnings
    })

# Vista para editar el perfil del administrador
@login_required
def editar_perfil_admin(request, user_id):
    # Obtienes al administrador logueado
    current_admin = request.user

    # Asegurarte de que el perfil del administrador esté creado
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)

    # Obtienes al usuario por el ID
    u = get_object_or_404(User, id=user_id)
    profile = u.profile  # El perfil asociado al usuario

    # Si el método es POST, validamos los formularios
    if request.method == 'POST':
        u_form = EditUserForm(request.POST, instance=u)  # Formulario de usuario
        p_form = EditProfileForm(request.POST, request.FILES, instance=profile)  # Formulario del perfil

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # Guardar los datos del usuario
            p_form.save()  # Guardar los datos del perfil

            # Verificamos si se ha cambiado la contraseña
            new_password = request.POST.get('password')
            if new_password:
                u.set_password(new_password)
                u.save()

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfilAdmin')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        u_form = EditUserForm(instance=u)  # Formulario para editar los datos del usuario
        p_form = EditProfileForm(instance=profile)  # Formulario para editar el perfil

    # Pasamos el formulario y el perfil al template
    return render(request, 'dashboard/usuarios/userProfile/editarPerfilAdmin.html', {
        'u_form': u_form,
        'p_form': p_form,
        'admin_profile': profileAdmin,  # Perfil del administrador
        'u': u,  # El usuario actual
        'profile': profile,  # El perfil completo del usuario
    })

# Vista para administrar usuarios
@login_required
def administrar_usuarios(request):
    return redirect("listaUsuarios")

# Vista para administrar artículos
@login_required
def administrar_articulos(request):
    return redirect('listaArticulos')

# Vista para administrar informes
@login_required
def administrar_informes(request):
    return redirect('listaInformes')



# --------------------------------------------------------------
# ADMIN MENSAJES
# --------------------------------------------------------------


@staff_member_required
def mensajes_admin(request):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    mensajes = MensajeContacto.objects.order_by("-creado")
    MensajeContacto.objects.filter(leido=False).update(leido=True)
    return render(request, "dashboard/mensajes/mensajes.html", {
        "admin_profile": profileAdmin,
        "mensajes": mensajes
    })
@staff_member_required
def ver_mensaje(request, id):
    current_admin = request.user
    profileAdmin, created = Profile.objects.get_or_create(user=current_admin)
    mensaje = MensajeContacto.objects.get(id=id)
    mensaje.leido = True
    mensaje.save()
    return render(request, "dashboard/mensajes/ver_mensaje.html", {
        "admin_profile": profileAdmin,
        "mensaje": mensaje,
    })
@staff_member_required
def eliminar_mensaje(request, id):
    MensajeContacto.objects.filter(id=id).delete()
    return redirect("mensajesAdmin")
