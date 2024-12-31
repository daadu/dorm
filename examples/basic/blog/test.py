from django.test import TestCase

from blog.models import Post


class TestPostModel(TestCase):
    def test_creating_object(self):
        post = Post()
        post.title = "Fake title"
        post.slug = "fake-title"
        post.post = "fake body"
        post.save()
