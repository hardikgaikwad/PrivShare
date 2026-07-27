from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse
from django.utils import timezone
from .models import EncryptedFile
from .utils import cleanup

class FileUploadView(APIView):
    def post(self, request):
        deleted_count = cleanup()
        if deleted_count > 0:
            print(f"Deleted {deleted_count} expired files.")

        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        obj = EncryptedFile.objects.create(
            file_name=uploaded_file.name,
            file=uploaded_file
        )

        download_url = f"{request.scheme}://{request.get_host()}/api/download/{obj.download_token}/"
        return Response({"download_url": download_url, "token": str(obj.download_token)}, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    def get(self, request, token):
        obj = get_object_or_404(EncryptedFile, download_token=token)

        # Check expiry
        if obj.expiry_time < timezone.now():
            return Response({"error": "File expired"}, status=status.HTTP_410_GONE)

        def file_iterator(file_obj, chunk_size=8192):
            file_obj.open('rb')
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            file_obj.close()
        
        response = StreamingHttpResponse(
            file_iterator(obj.file),
            content_type='application/octet-stream',
        )
        response['Content-Disposition'] = f'attachment; filename="{obj.file_name}"'
        return response