from django.db import models
import uuid
import secrets
from django.utils import timezone
from datetime import timedelta

MB = 1024 * 1024

class Signup(models.Model):
    regid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=50,unique=True)        
    password=models.CharField(max_length=10)
    mobile=models.CharField(max_length=15)
    status=models.IntegerField()
    role=models.CharField(max_length=10)
    info=models.CharField(max_length=50)
    # Storage quota fields
    storage_used  = models.IntegerField(default=0)           # bytes consumed
    storage_limit = models.IntegerField(default=300 * MB)    # 300 MB in bytes



class ShareNotes(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(default="No Description")
    file = models.FileField(upload_to='documents/')
    original_filename = models.CharField(max_length=255)

    file_size = models.BigIntegerField(default=0)   # original file size in bytes
    owner = models.CharField(max_length=100)

    upload_time = models.DateTimeField(auto_now_add=True)

    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    encryption_key = models.TextField(null=True)
    is_shared = models.BooleanField(default=False)


def _default_expiry():
    return timezone.now() + timedelta(hours=24)


class SharedLink(models.Model):
    file = models.ForeignKey(ShareNotes, on_delete=models.CASCADE, related_name="shared_links")
    token = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField(default=_default_expiry)
    max_downloads = models.PositiveIntegerField(default=5)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_exhausted(self):
        return self.download_count >= self.max_downloads

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_exhausted

    def __str__(self):
        return f"SharedLink({self.file.title}) — {'valid' if self.is_valid else 'invalid'}"