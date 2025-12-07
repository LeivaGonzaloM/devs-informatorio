from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from posts.models import Post

from .forms import UserReportForm
from django.utils import timezone




# Registrar Usuario
def signup(request):
    if request.method == 'GET':
        return render(request, 'users/register.html', {
            'hide_nav_footer': True
        })

    # POST
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    fullname = request.POST.get('fullname', '').strip()

    # Validaciones
    if not username or not email or not password1 or not password2:
        return render(request, 'users/register.html', {
            'error': 'Todos los campos son obligatorios.',
            'hide_nav_footer': True
        })

    if password1 != password2:
        return render(request, 'users/register.html', {
            'error': 'Las contraseñas no coinciden.',
            'hide_nav_footer': True
        })

    if User.objects.filter(username=username).exists():
        return render(request, 'users/register.html', {
            'error': 'El usuario ya existe.',
            'hide_nav_footer': True
        })

    if User.objects.filter(email=email).exists():
        return render(request, 'users/register.html', {
            'error': 'El email ya está registrado.',
            'hide_nav_footer': True
        })

    # Crear usuario
    user = User.objects.create_user(username=username, email=email, password=password1)
    user.save()

    # Actualizar el full_name en el profile existente
    if hasattr(user, 'profile'):
        user.profile.full_name = fullname
        user.profile.save()

    # Login automático
    login(request, user)

    return redirect('home')



# Cerrar Sesión
@login_required
def signout(request):
    logout(request)
    return redirect('home')


# Iniciar Sesión
def signin(request):
    if request.method == 'GET':
        return render(request, 'users/login.html', {
            'form': AuthenticationForm,
            'hide_nav_footer': True
        })

    else:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'users/login.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecta'
            })

        # 🔥 CHEQUEO DE BLOQUEO AQUÍ
        profile = user.profile
        if profile.is_currently_blocked:
            remaining = profile.blocked_until - timezone.now()
            minutes = max(1, int(remaining.total_seconds() // 60))
            return render(request, 'users/login.html', {
                'form': AuthenticationForm,
                'error': f'Tu cuenta está bloqueada. Tiempo restante: {minutes} minutos.'
            })

        # 🔥 Login normal
        login(request, user)
        return redirect('home')


# PERFIL
@login_required
def profileView(request, username=None):
    current_user = request.user
    if username and username != current_user.username:
        user_profile = User.objects.filter(username=username).first()
        if not user_profile:
            return redirect('profile')  # Redirige si el usuario no existe
        is_own_profile = False
    else:
        user_profile = current_user
        is_own_profile = True

    posts = Post.objects.filter(user=user_profile)
    profile, created = Profile.objects.get_or_create(user=user_profile)


    return render(request, 'users/profile/profile.html', {
        'user_profile': user_profile,
        'profile': profile,
        'posts': posts,
        'is_own_profile': is_own_profile,
    })


# Editar datos del usuario
@login_required
def editProfile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')  # o a donde quieras
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile/editUser.html', context)

# Sistema report User
@login_required
def reportUser(request, user_id):
    reported_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.save()

            return redirect('profile')
    else:
        form = UserReportForm()

    return render(request, 'users/reportUser/reportUser.html', {
        'reported_user': reported_user,
        'form': form
    })
      