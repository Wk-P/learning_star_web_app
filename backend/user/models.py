from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255, blank=False, nuill=False, unique=True)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True, db_index=True)
    
