from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Docs(models.Model):
	address = models.CharField(max_length=200)