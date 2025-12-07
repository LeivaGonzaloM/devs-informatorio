from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import MessageForm
from .models import Message, get_chat_messages
from django.db.models import Q, Max
from django.utils.timezone import now


@login_required
def inbox(request):
    # Obtener lista de usuarios con los que se habló
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))

    # Agrupar por usuario (otro participante)
    chat_data = {}
    for msg in messages:
        other = msg.receiver if msg.sender == request.user else msg.sender

        if other not in chat_data or msg.timestamp > chat_data[other]["last"].timestamp:
            chat_data[other] = {
                "other": other,
                "last": msg
            }

    chats = list(chat_data.values())

    return render(request, "messages/inbox/inbox.html", {
        "chats": chats
    })


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    current_user = request.user

    messages = Message.objects.filter(
        sender=current_user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=current_user
    )
    messages = messages.order_by('timestamp')

    return render(request, "messages/chat/chat.html", {
        "messages": messages,
        "other": other_user,
    })


@login_required
def send_message(request, username):
    if request.method == "POST":
        other = get_object_or_404(User, username=username)

        content = request.POST.get("content")
        if content.strip() != "":
            Message.objects.create(
                sender=request.user,
                receiver=other,
                content=content
            )

        return redirect("chat", username=other.username)

    return redirect("inbox")