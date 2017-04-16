from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Docs(models.Model):
	address = models.CharField(max_length=200)

class UserTag(models.Model):
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name + " " + self.category