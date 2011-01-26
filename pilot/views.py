import datetime
import logging
import mimetypes
import os.path
import zipfile
import tarfile
import re
import string
from services import identity, storage, annotate 
from models import Philes
from tempfile import mkdtemp
from obj import DigitalObject
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.forms.models import save_instance
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

def default(request, display):
    phils = Philes.objects.filter(owner='dmc186')
    myobj = []
    for p in phils:
        myobj.append(DigitalObject("title", p.identifier, "type", "1", p.date_updated))
    #myobj.append(DigitalObject("9780271032689_09_CH04_p113-148.pdf", "42409/9177pv46w", "pdf", "10", "18-Aug-2001"))
    mylist = annotate.query("SELECT ?title WHERE { ?subj <http://purl.org/dc/elements/1.1/title> ?title }")
    for tit in mylist:
        print "title: %s" % tit

    
    return render_to_response('index.html', {'objects': myobj, 'display': display})

def get_identifier(request):
    id = identity.mint()

    if (identity.validate(id) ):
        return render_to_response('identifier.html', {'identifier' : id });
    else:
        return render_to_response('identifier.html', {'identifier' : "0" });        

def get_fixity(request):
    fil = "/dlt/users/dmc186/dltmap.js"
    algorithm = 'md5'
    h = fixity.generate(fil, algorithm)
    return render_to_response('fixity.html', {'fixity' : h, 'filename': fil, 'algorithm': algorithm});

def new_object(request, type):
    batch = True
    r = 5
    if type == 'object':
        batch = False
        r = 1
    meta_values = ['select meta type', 'contributor', 'coverage', 
        'creator', 'date', 'description', 'format', 'identifier', 
        'language', 'publisher', 'relation', 'rights', 'source', 
        'subject', 'title', 'type']
    
    return render_to_response('ingest.html', {'meta': meta_values, 'batch': batch, 'range': range(r)});


def handle_file_upload(udir, f):
    fname = os.path.join(udir, f.name)
    print "saving %s" % fname
    destination = open(fname, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


""" 
handles unpacking many archive types from
the is_archive function
afile is the location of the archived file
atype is the type of file from the content_type
    passed via form
"""
def unpack_archive(afile, atype):
    tmp_pth = os.path.dirname(afile)
    print "path:%s" % tmp_pth

    suffix = atype.split("/")    
    if len(suffix) != 2:
        return False
    
    if suffix[1] == 'zip':  
        print "zip"
        af = zipfile.ZipFile(afile, "r")
    elif suffix[1] == 'x-tar':
        print "tar"
        af = tarfile.open(afile, "r")
    elif suffix[1] == 'x-gzip':
        print "gzip"
        af = tarfile.open(afile, "r:gz")
    elif suffix[1] == 'x-bzip2':
        print "bzip2"
        af = tarfile.open(afile, "r:bz2")
    else:
        print "no match for archive: %s" % suffix[1]
        return False

    # Sanitize - ensure no absolute paths or '../' 
    if suffix[1] == 'zip':
        for name in af.namelist():
            if os.path.isabs(name) or re.match('^\.\.', name):
                print "file no good: %s" % name
                return False
    else:
        for f in af:
            if os.path.isabs(f.name) or re.match('^\.\.', f.name):
                print "file no good: %s" % f.name
                return False

    af.extractall(tmp_pth)
    af.close()

def is_archive(ct):
    archive_types = ['application/x-gzip', 'application/x-tar', 'application/zip', 
        'application/x-bzip2']
    for ty in archive_types:
        if ty == ct:
            return True

    return False

def upload_object(request):
    if request.method == 'POST':
        
        ark = identity.mint_new()
        print "posting:%s" % ark
        
        uploaddir = mkdtemp()
        print "dir:%s" % uploaddir

        # loop over the files to upload
        for i in range(int(request.POST.get('upload_count'))):
            f = request.FILES['file_'+str(i+1)]
            cb_key = 'unzip_cb_' + str(i+1)
            # if user does not want to unpack or just regular file upload
            print "index:%s" % str(i+1)
            print "file:%s" % f 
            print "filetype:%s" % f.content_type
            # unpacking a file for user and uploading that
            handle_file_upload(uploaddir, f)
            if request.POST.has_key(cb_key) == False and is_archive(f.content_type):
                print "unpack the biatch"
                aname = os.path.join(uploaddir, f.name)
                unpack_archive(aname, f.content_type)
            print "------------\n"

        # done uploading the files 

#        repopath = storage.ingest_directory(ark, uploaddir)
#        identity.bind(ark, repopath, 'dmc186')
#
#        assertions = []
#        # loop over metadata to store
#        for i in range(int(request.POST.get('metadata_count'))):
#            k = request.POST.get('meta_type_'+str(i+1))
#            v = request.POST.get('meta_value_'+str(i+1))
#            print "%s %s=>%s" % (ark, k, v)
#            assertion = (ark, ("dc", "http://purl.org/dc/elements/1.1/", k), v) 
#            assertions.append(annotation)
#        annotation.add(ark, assertions)
       
        # done adding metadata 
        return HttpResponseRedirect('/pilot/list')

    return render_to_response('ingest.html', {'batch': False});

# A view to report back on upload progress:
def upload_progress(request):
    print "even called?"
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = None
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']

    print "progress_id:%s" % progress_id

    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        json = simplejson.dumps(data)
        print "json:%s" % json
        return HttpResponse(json)
    else:
        return HttpResponseBadRequest('Server Error: You must provide X-Progress-ID header or query param.')

def management(request, arkid):
    return render_to_response('management.html', {'arkid': arkid})

def screenshots(request):
    return render_to_response('screenshots.html');
