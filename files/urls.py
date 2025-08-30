from django.urls import path
from .views import FileUploadView, FileDownloadView

urlpatterns = [
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/download/<uuid:token>/', FileDownloadView.as_view(), name='file-download'),
]
