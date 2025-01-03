# dorm

[![PyPI - Version](https://img.shields.io/pypi/v/dorm-project)](https://pypi.org/project/dorm-project/)
[![PyPI - Status](https://img.shields.io/pypi/status/dorm-project)](https://pypi.org/project/dorm-project/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dorm-project)](https://pypi.org/project/dorm-project/)
[![PyPI - Versions from Framework Classifiers](https://img.shields.io/pypi/frameworkversions/django/dorm-project)](https://pypi.org/project/dorm-project/)
[![GitHub License](https://img.shields.io/github/license/daadu/dorm)](https://github.com/daadu/dorm/blob/master/LICENSE)
[![ci](https://github.com/daadu/dorm/actions/workflows/ci.yml/badge.svg)](https://github.com/daadu/dorm/actions/workflows/ci.yml)
[![cd](https://github.com/daadu/dorm/actions/workflows/cd.yml/badge.svg)](https://github.com/daadu/dorm/actions/workflows/cd.yml)
[![Stars](https://img.shields.io/github/stars/daadu/dorm?logo=github)](https://github.com/daadu/dorm/stargazers)

**dorm** is a minimal wrapper around Django that allows you to use its ORM 
independently—no need for the full Django framework. Quickly integrate Django's 
robust ORM into non-Django projects with a simple settings.py file.

> **Note:** This project is under active development. Use with caution.

## Why dorm?
The Django ORM is rich with features like automatic schema migrations and effortless joins. 
Other python ORMs, like SQLAlchemy, often felt less intuitive in comparison.

The idea for dorm emerged from a desire to use Django's ORM without unnecessary overhead 
like `manage.py`, `views.py`, or complex settings. With dorm, you get the power of Django 
ORM, simplified for standalone use.

> **Note:** Since `dorm` is a lightweight wrapper around Django, all of Django's features 
> remain accessible if you choose to use them. `dorm` ensures you can leverage Django's ORM 
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

#### 2. Setup dorm

Call the `dorm.setup()` method in your project's entry point (e.g., `main.py`, `app.py`, or the script that starts 
your application) to initialize the Django ORM and set up the necessary database connections. This step is essential
for using the ORM independently of the full Django framework.

If you're interacting with the project via the `dorm` CLI (e.g., running migrations or using the shell or any 
custom Django management command), `dorm.setup()` is automatically called for you.

> **Note:** Ensure that models are imported **after** calling `dorm.setup()` to avoid any initialization issues.

> **Note:** Ensure you call `dorm` or your entrypoint from the project root (where the settings.py is).
> If you want to call from somewhere else, then explicitly pass `settings_dir` to `dorm.setup(settings_dir=...)`

Here's how you might set it up in your entry point:
```python
# entrypoint - main.py, script.py, project.__init__.py etc
import dorm

def main():
    dorm.setup()
    
    # You can start importing and using your models from here...
    

if __name__ == "__main__":
    main() 
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
Use `dorm` CLI to manage migrations (or any django management command - like `shell`, `test`, `dbshell`, etc:
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
Run test with [Django test runner](https://docs.djangoproject.com/en/5.1/topics/testing/overview/#running-tests) via `dorm` CLI:
```shell
dorm test
```

--- 

## Future Plans
- Features to make `dorm` feasible with other web framework - with proper connection pooling and transactional requests. [full](https://www.reddit.com/r/django/comments/1hqy923/comment/m4tw22n/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
- Allow users to access admin site