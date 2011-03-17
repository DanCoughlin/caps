from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # upload new object 
    (r'^pilot/(?P<type>(object|batch))/new', 'caps.pilot.views.new_object'),

    # display dashboard
    (r'^pilot/(?P<display>(list|icons))', 'caps.pilot.views.default'),


    # update metadata attribute
    (r'^pilot/meta/update$', 'caps.pilot.views.meta_update'), 

    # remove metadata attribute
    (r'^pilot/meta/remove/(?P<metaid>\d+)/$', 'caps.pilot.views.remove_metadata'),

    # add metadata attribute
    (r'^pilot/meta/add/$', 'caps.pilot.views.add_metadata'),

    # run an audit on an object
    (r'^pilot/audit/(?P<arkid>ark:(.)*)$', 'caps.pilot.views.audit'),

    # view object event log
    (r'^pilot/log/(?P<arkid>ark:(.)*)$', 'caps.pilot.views.get_log'),
    #(r'^pilot/(?P<arkid>ark:/\d{5}/(.)*)\/log$', 'caps.pilot.views.get_log'),

    # view versions for object 
    (r'^pilot/versions/(?P<arkid>ark:(.)*)$', 'caps.pilot.views.get_versions'),

    # search for objects
    (r'^pilot/search/(?P<keyword>(.)*)$', 'caps.pilot.views.search'),

    # get autocomplete for metadata searching
    (r'^pilot/autocomplete/$', 'caps.pilot.views.autocomplete'),

    #/pilot/upload_progress/?X-Progress-ID=0a8ee3eb055b6f043ed48c8208c9c623
    (r'^pilot/upload_progress/$', 'caps.pilot.views.upload_progress'),

    # upload a batch object
    (r'^pilot/upload_batch$', 'caps.pilot.views.upload_batch'),

    # upload single objects at a time
    (r'^pilot/upload', 'caps.pilot.views.upload_object'),

    # get the files within an object
    (r'^pilot/filetree', 'caps.pilot.views.filetree'),

    # view object - order of this matters
    (r'^pilot/(?P<arkid>ark:/\d{5}/(.)*)$', 'caps.pilot.views.management'),

    # go to default view if you hit /pilot/ or /
    (r'^pilot', 'caps.pilot.views.default'),
    (r'^$', 'caps.pilot.views.default'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/(.*)', admin.site.root),

    # login while in django dev server
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),


    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/var/www/django/caps/site_media/'}    ),
)
