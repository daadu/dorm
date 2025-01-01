# dorm

[![PyPI - Version](https://img.shields.io/pypi/v/dorm-project)](https://pypi.org/project/dorm-project/)


**dorm** is a lightweight wrapper around Django that provides a minimal 
interface to its ORM. This package allows you to quickly integrate Django's 
powerful ORM into your project with minimal configuration—simply add a `settings.py`
file to the project root and you're ready to start using it.

> The project is still under active development, use it at your own risk.
> 
> Tested only against:
> - Python: 3.10, 3.11, 3.12
> - Django: 5.0

Familiarity with Django (especially about [Models and databases](https://docs.djangoproject.com/en/5.1/topics/db/)) is expected to use this project.

## Initial motivation

I’ve always been a big fan of the Django ORM, especially its features like 
automatic schema migrations and the ability to perform joins without writing
raw SQL.

Over time, I’ve used it outside of full Django projects whenever I needed to 
interact with a database. Given the richness of Django’s ORM, I found other 
standalone ORMs (like SQLAlchemy) to be lacking in comparison. During these 
experiences, I kept wondering: what if I could use just the ORM, without the 
need for `manage.py`, `views.py`, `urls.py`, or any unnecessary entries 
in `settings.py`?

That’s how the idea for this project was born.

## Basic Usage

1. Install dorm

    ```shell
    pip install dorm-project
    ```

2. Initialize your project to use dorm, by adding `settings.py` to the project root

    ```shell
    cd <proj-root>
    touch settings.py # << at least add INSTALLED_APPS and DATABASES
    ```

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

    > TODO: implement `dorm init` command that scaffolds `settings.py` file

3. Call `dorm.setup()` at the entry point of your project, this will ensure that django setup is done properly before usage.
This should be called at least once before any import of Django models.

    ```python
    import dorm
    
    if __name__ == "__main__":
        dorm.setup()
        ...
    ```

4. Add `models.py` to a new or existing package (this package will be considered as a Django app, check point 5 below), and add some models in it

    ```shell
    mkdir -p <my-package>
    touch <my-package>/models.py
    ``` 

    ```python
    # <my-package>/models.py
    
    from django.db import models
    
    
    class Post(models.Model):
        title: str = models.CharField(max_length=100)
        slug: str = models.SlugField(unique=True)
        body: str = models.TextField()
    ```

5. Add the package with `models.py` to `INSTALLED_APPS` in `settings.py`

    ```python
    # settings.py
    ...
    INSTALLED_APPS = [
        ...,
        "<my-package>",
        ...,
    ]
    ...
    ```

6. Make migrations and migrate with `dorm` commands (can run all django management commands with it - like `shell`, `test`, `dbshell`, etc)

    ```shell
    dorm makemigrations
    dorm migrate
    ```

7. Create some objects with `dorm shell`

    ```shell
    dorm shell
    ...
    >>> from blog.models import Blog
    >>> blog = Blog(title="Hello", body="... World!!", slug="hello-world")
    >>> blog.save()
    >>> Blog.objects.all()
    ```
