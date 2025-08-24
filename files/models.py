from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class EncryptedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    encrypted_data = models.BinaryField()
    iv = models.BinaryField()
    tag = models.BinaryField()
    key = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def default_expiry_time():
        return timezone.now() + timedelta(hours=6)
    expiry_time = models.DateTimeField(default=default_expiry_time)
    download_token = models.UUIDField(default=uuid.uuid4, unique=True)