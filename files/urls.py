from django.urls import path
from .views import FileDownloadView, FileUploadView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('download/<uuid:token>/', FileDownloadView.as_view(), name='file-download'),
]