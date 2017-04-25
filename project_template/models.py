from __future__ import unicode_literals

from django.db import models


class TwitterUser(models.Model):
    name = models.CharField(max_length=128)
    twitter_handle = models.CharField(max_length=128)
    profile_image = models.CharField(max_length=500, null=True)  # uri of their profile picture
    user_type = models.CharField(max_length=100, null=True) # person or organization


class Tag(models.Model):
    name = models.CharField(max_length=128)


class UserTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tag_set")
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, related_name="user_set")
