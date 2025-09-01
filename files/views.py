from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import EncryptedFile
from .utils import encrypt_file, decrypt_file, cleanup

class FileUploadView(APIView):
    def post(self, request):
        deleted_count = cleanup()
        if deleted_count > 0:
            print(f"Deleted {deleted_count} expired files.")
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        file_bytes = uploaded_file.read()
        encrypted_data, key, iv, tag = encrypt_file(file_bytes)

        obj = EncryptedFile.objects.create(
            file_name=uploaded_file.name,
            encrypted_data=encrypted_data,
            key=key,
            iv=iv,
            tag=tag
        )

        download_url = f"{request.scheme}://{request.get_host()}/api/download/{obj.download_token}/"
        return Response({"download_url": download_url}, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    def get(self, request, token):
        obj = get_object_or_404(EncryptedFile, download_token=token)

        # Check expiry
        if obj.expiry_time < timezone.now():
            return Response({"error": "File expired"}, status=status.HTTP_410_GONE)

        try:
            decrypted_data = decrypt_file(
                bytes(obj.encrypted_data),
                bytes(obj.key),
                bytes(obj.iv),
                bytes(obj.tag),
            )
            response = HttpResponse(decrypted_data, content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{obj.file_name}"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
