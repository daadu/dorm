# dorm

[![PyPI - Version](https://img.shields.io/pypi/v/dorm-project)](https://pypi.org/project/dorm-project/)

**dorm** is a minimal wrapper around Django that allows you to use its ORM 
independently—no need for the full Django framework. Quickly integrate Django's 
robust ORM into non-Django projects with a simple settings.py file.

> Note: This project is under active development. Use with caution.
> 
> Tested on:
> - Python: 3.10, 3.11, 3.12
> - Django: 5.0

## Why dorm?
The Django ORM is rich with features like automatic schema migrations and effortless joins. 
Other python ORMs, like SQLAlchemy, often felt less intuitive in comparison.

The idea for dorm emerged from a desire to use Django’s ORM without unnecessary overhead 
like `manage.py`, `views.py`, or complex settings. With dorm, you get the power of Django 
ORM, simplified for standalone use.

> **NOTE:** Since `dorm` is a lightweight wrapper around Django, all of Django's features 
> remain accessible if you choose to use them. `dorm` ensures you can leverage Django’s ORM 
> with minimal setup and footprint.

---

## Installation

```bash
pip install dorm-project "django>=5.1.0,<5.2.0" 
# Install Django to a specific version to ensure compatibility and avoid potential issues.  
```

## Quick Start

#### 1. Add a settings.py file
Automatically (recommended) add using `dorm init` command:
```bash
cd <proj-root>
dorm init 
```
**OR**

Manually add `settings.py` file, ensure `INSTALLED_APPS` and `DATABASES` values are set:
```python
# <proj-root>/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

INSTALLED_APPS = []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

#### 2. Set up dorm
Initialize the ORM in your project's entry point:
```python
# entrypoint - main.py, script.py, etc
import dorm

if __name__ == "__main__":
    dorm.setup()
```

#### 3. Define models
Create a `models.py` in a package and add Django models:
```shell
mkdir -p blog
touch blog/models.py
```
Example model:
```python
# blog/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    body = models.TextField()
```

#### 4. Register your app
Add your package to `INSTALLED_APPS` in `settings.py`:
```python
# <proj-root>/settings.py
INSTALLED_APPS = [
    "blog",
]
```

#### 5. Run migrations
Use `dorm` cli to manage migrations (or any django management command - like `shell`, `test`, `dbshell`, etc:
```shell
dorm makemigrations
dorm migrate
```

#### 6. Use the ORM
Access your models in an interactive shell:
```shell
dorm shell
```
Example:
```pycon
>>> from blog.models import Post
>>> post = Post(title="Hello", slug="hello-world", body="This is dorm!")
>>> post.save()
>>> Post.objects.all()
```

#### 7. Write `unittest` using the ORM
Example:
```python
# blog/tests.py
from django.test import TestCase

from blog.models import Post

class TestPostModel(TestCase):
    def test_creating_object(self):
        post = Post()
        post.title = "Fake title"
        post.slug = "fake-title"
        post.post = "fake body"
        post.save()
```
Run test with [Django test runner](https://docs.djangoproject.com/en/5.1/topics/testing/overview/#running-tests) via `dorm` cli:
```shell
dorm test
```

--- 

## Future Plans
- Features to make `dorm` feasible with other web framework - with proper connection pooling and transactional requests. [full](https://www.reddit.com/r/django/comments/1hqy923/comment/m4tw22n/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) 