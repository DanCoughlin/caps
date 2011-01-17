from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^caps/', include('caps.foo.urls')),
    (r'^pilot/(?P<type>(object|batch))/new', 'caps.pilot.views.new_object'),
    (r'^pilot/(?P<display>(list|icons))', 'caps.pilot.views.default'),
    (r'^pilot/ark:/(?P<arkid>(.*))$', 'caps.pilot.views.management'),
    
    #/pilot/upload_progress/?X-Progress-ID=0a8ee3eb055b6f043ed48c8208c9c623
    (r'^pilot/upload_progress/$', 'caps.pilot.views.upload_progress'),
    (r'^getIdentifier', 'caps.pilot.views.get_identifier'),
    (r'^getFixity', 'caps.pilot.views.get_fixity'),
    (r'^pilot/upload', 'caps.pilot.views.upload_object'),
    (r'^pilot/screenshots', 'caps.pilot.views.screenshots'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/var/www/django/site_media/'}    ),
)
