
from django.db import models
# Create your models here.

class Companies(models.Model):
    clubbed_name = models.CharField(max_length=150)
    insurer = models.CharField(max_length=500)
    name = models.CharField(max_length=10)


class Lob(models.Model):
     lob = models.JSONField(null=True, blank=True)


class Categories(models.Model):
    clubbed_name = models.CharField(max_length=150)
    category = models.CharField(max_length=10)

