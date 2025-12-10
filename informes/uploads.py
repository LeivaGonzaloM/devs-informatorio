import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string

@csrf_exempt
def ckeditor5_upload(request):
    """
    Endpoint para subir archivos desde CKEditor 5
    """
    if request.method == "POST" and request.FILES.get("upload"):
        upload = request.FILES["upload"]
        
        filename = get_random_string(16) + "_" + upload.name
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, filename)
        
        with open(upload_path, "wb+") as f:
            for chunk in upload.chunks():
                f.write(chunk)
        
        url = settings.MEDIA_URL + "uploads/" + filename
        return JsonResponse({
            "uploaded": 1,
            "fileName": filename,
            "url": url
        })
    
    return JsonResponse({"uploaded": 0, "error": {"message": "No file uploaded"}}, status=400)
