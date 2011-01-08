import os
import sys
sys.path.append('/var/www/django')
sys.path.append('/var/www/django/caps')

os.environ['DJANGO_SETTINGS_MODULE'] = 'caps.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

