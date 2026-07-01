from django.db import models

# Create your models here.
class User(models.Model):
  username = models.CharField(max_length=100)
  email =  models.EmailField(unique=True)
  password = models.CharField(max_length=255)
  profile_picture = models.URLField(max_length=500, blank=True, null=True)

  def __str__(self):
    return self.username
