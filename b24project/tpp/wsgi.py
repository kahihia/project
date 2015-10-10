"""
WSGI config for tpp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import newrelic.agent
newrelic.agent.initialize('/var/www/b24app/newrelic.ini')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tpp.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)