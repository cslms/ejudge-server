from . import fixes as _fixes
from .__meta__ import __author__, __version__
from .celery import app as celery_app

__all__ = ['celery_app']
