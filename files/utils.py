from django.utils import timezone
from .models import EncryptedFile

def cleanup():
    now = timezone.now()
    expired_files = EncryptedFile.objects.filter(expiry_time__lt=now)
    count = expired_files.count()
    if count > 0:
        expired_files.delete()
    return count
