import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

def default_expiry():
    return timezone.now() + timedelta(hours=6)

class EncryptedFile(models.Model):
    download_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file_name = models.CharField(max_length=255)
    encrypted_data = models.BinaryField()
    key = models.BinaryField()
    iv = models.BinaryField()
    tag = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"{self.file_name} ({self.download_token})"
