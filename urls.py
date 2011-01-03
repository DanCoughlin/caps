from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^caps/', include('caps.foo.urls')),
    (r'^pilot/(?P<type>(object|batch))/new', 'caps.pilot.views.new_object'),
    (r'^getIdentifier', 'caps.pilot.views.get_identifier'),
    (r'^getFixity', 'caps.pilot.views.get_fixity'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/var/www/django/site_media/'}    ),
    #(r'', 'caps.pilot.views.default')
)
