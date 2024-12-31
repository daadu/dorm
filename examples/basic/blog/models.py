from datetime import datetime

from django.db import models


class Post(models.Model):
    title: str = models.CharField(max_length=100)
    slug: str = models.SlugField(unique=True)
    post: str = models.TextField()
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post(pk={self.pk}, {self.slug})"
