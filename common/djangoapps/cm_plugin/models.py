from django.db import models

class XModule_Metadata_Cache(models.Model):
    url = models.CharField(max_length=255, unique=True)
    cm_id = models.CharField(max_length=255)
    start = models.DateTimeField()
    due = models.DateTimeField(null=True)
    obj_type = models.CharField(max_length=100)
    course = models.CharField(max_length=500)
    title = models.CharField(max_length=100, null=True)  
    state = models.CharField(max_length=10)
    video_url = models.CharField(max_length=100, null=True)
    posted = models.BooleanField()

# Create your models here.
class HealthCheck(models.Model):
    test = models.CharField(max_length=200)
