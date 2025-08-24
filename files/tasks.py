from background_task import background
from django.utils import timezone
from .models import EncryptedFile

@background(schedule=3600)
def delete_expired_files():
    EncryptedFile.objects.filter(expiry_time__lt=timezone.now()).delete()