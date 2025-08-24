from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import EncryptedFile
from .utils import encrypt_file, decrypt_file
from datetime import timezone

# Create your views here.

class FileUploadView(APIView):
    def post(self, request):
        uploaded_file = request.FILES['file']
        file_bytes = uploaded_file.read()
        encrypted_data, key, iv, tag = encrypt_file(file_bytes)

        obj = EncryptedFile.objects.create(
            file_name=uploaded_file.name,
            encrypted_data=encrypted_data,
            iv=iv,
            tag=tag,
            key=key
        )

        download_url = f"{request.build_absolute_url('/download/')}{obj.download_token}/"
        return Response({"download_url": download_url}, status=status.HTTP_201_CREATED)
    
class FileDownloadView(APIView):
    def get(Self, request, token):
        obj = get_object_or_404(EncryptedFile, download_token=token)
        if obj.expiry_time < timezone.now():
            return Response({"error": "File expired"}, status=status.HTTP_410_GONE)
        decrypted_data = decrypt_file(obj.encrypted_data, obj.key, obj.iv, obj.tag)
        response = Response(decrypted_data, content_type="application/octet-stream")
        response['Content-Disposition'] = f'attachment; filename="{obj.file_name}"'
        return response