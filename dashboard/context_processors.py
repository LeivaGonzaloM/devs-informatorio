from users.models import UserReport
from dashboard.models import MensajeContacto

def admin_notifications(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    nuevos_reportes = UserReport.objects.filter(visto_admin=False).count()
    nuevos_mensajes = MensajeContacto.objects.filter(leido=False).count()

    return {
        "new_reports_count": nuevos_reportes,
        "new_messages_count": nuevos_mensajes,
        "has_notifications": nuevos_reportes > 0 or nuevos_mensajes > 0,
        "total_notifications": nuevos_reportes + nuevos_mensajes,
    }
