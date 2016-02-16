# -*- config: utf-8 -*-
from __future__ import unicode_literals
from configurations.wsgi import get_wsgi_application
import os

"""
WSGI config for league project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhea.settings')
application = get_wsgi_application()
