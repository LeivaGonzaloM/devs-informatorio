from django.shortcuts import render, redirect, get_object_or_404
from .models import Informe, CommentInforme
from .forms import InformeForm
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden


# Create your views here.
def informes(request):
    informes = Informe.objects.all()
    return render(request, 'informes/informes.html',{
        "informes" : informes,}
                  )


@login_required
def crear_informe(request):
    if request.method == "POST":
        form = InformeForm(request.POST, request.FILES)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.user = request.user
            informe.save()
            return redirect('informes')  # Ajusta según tu URL
        else:
            return render(request, "informes/crud/crearInforme.html", {
                "form": form,
                "error": "Revisa los campos."
            })

    form = InformeForm()
    return render(request, "informes/crud/crearInforme.html", {"form": form})



def detalleInforme(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    # POST -> crear comentario (desde el form normal)
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content", "").strip()
        gif_url = request.POST.get("gif_url") or None

        if content:
            CommentInforme.objects.create(
                user=request.user,
                post=informe,
                content=content,
                gif_url=gif_url
            )
        return redirect("detalleInforme", pk=pk)

    # listar comentarios del informe (usar related_name 'comments')
    comments = informe.comments.all().order_by("-dateCreated")

    return render(request, "informes/informeDetail.html", {
        "informe": informe,
        "comments": comments,
    })


def editarInforme(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    if request.user != informe.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar este informe.")
        return redirect("detalleInforme", pk=pk)

    if request.method == "POST":
        informe.title = request.POST.get("title", informe.title)
        informe.description = request.POST.get("description", informe.description)
        if request.FILES.get("image"):
            informe.image = request.FILES.get("image")
        informe.last_edited = now()
        informe.edited_by = request.user
        informe.save()
        messages.success(request, "Informe actualizado.")
        return redirect("detalleInforme", pk=pk)

    return render(request, "informes/crud/editarInforme.html", {"informe": informe})


def eliminarInforme(request, pk):
    informe = get_object_or_404(Informe, pk=pk)

    if request.user != informe.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar este informe.")
        return redirect("detalleInforme", pk=pk)

    if request.method == "POST":
        informe.delete()
        messages.success(request, "Informe eliminado.")
        return redirect("informes")  # ajustá al nombre de tu lista

    # si querés confirmación por GET:
    return render(request, "informes/crud/confirmarEliminarInforme.html", {"informe": informe})


# ---- Comentarios: editar/eliminar vía AJAX (fetch desde el JS del template) ----

@login_required
def editarComentarioInforme(request, pk):
    # pk aquí es el id del comentario
    comment = get_object_or_404(CommentInforme, pk=pk)
    if request.user != comment.user and not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "No autorizado."}, status=403)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse({"success": False, "error": "Contenido vacío."})
        comment.content = content
        comment.save()
        return JsonResponse({"success": True, "content": comment.content})
    return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)


@login_required
def eliminarComentarioInforme(request, pk):
    # pk aquí es id del comentario
    comment = get_object_or_404(CommentInforme, pk=pk)
    if request.user != comment.user and not request.user.is_superuser:
        return JsonResponse({"success": False, "error": "No autorizado."}, status=403)

    if request.method == "POST":
        comment.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)