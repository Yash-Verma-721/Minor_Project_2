from django.db import models
import uuid

class Signup(models.Model):
    regid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=50,unique=True)        
    password=models.CharField(max_length=10)
    mobile=models.CharField(max_length=15)
    status=models.IntegerField()
    role=models.CharField(max_length=10)
    info=models.CharField(max_length=50)



class ShareNotes(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(default="No Description")
    file = models.FileField(upload_to='documents/')
    original_filename = models.CharField(max_length=255)

    owner = models.CharField(max_length=100)

    upload_time = models.DateTimeField(auto_now_add=True)

    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    encryption_key = models.TextField(null=True)
    is_shared = models.BooleanField(default=False)