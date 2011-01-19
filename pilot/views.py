import datetime
import logging
import mimetypes
import os.path
from services import identity, storage, annotate 
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
    myobj = []
    myobj.append(DigitalObject("annual report.pdf", "42409/6c510c54b", "pdf", "1", "08:45am"))
    myobj.append(DigitalObject("certificate.txt", "42409/p829jb983", "txt", "8", "05-January"))
    myobj.append(DigitalObject("EMC XAM Developers Pack 1.0(2).zip", "42409/zj91v4776", "zip", "21", "01-January"))
    myobj.append(DigitalObject("my office.jpg", "42409/nn01sf24b", "image/jpg", "1", "01-May-2010", "image1"))
    myobj.append(DigitalObject("FFLBLog.txt", "42409/8347n589v", "txt", "4", "13-Jan-2010"))
    myobj.append(DigitalObject("github", "42409/4929jq005", "folder", "1005", "15-Jun-2009"))
    myobj.append(DigitalObject("mug shot.jpg", "42409/0b17c601v", "image/jpg", "2", "28-Oct-2008", "image3"))
    myobj.append(DigitalObject("a9e00a035b71173b348cd735c35.pdf", "42409/9w9996157", "pdf", "1", "27-Nov-2005"))
    myobj.append(DigitalObject("9780271032689_02_FM02_pv-vi.pdf", "42409/p494ss70q", "pdf", "1", "05-Oct-2006"))
    myobj.append(DigitalObject("Meeting Minutes", "42409/z0776s284", "folder", "501", "14-Mar-2006"))
    myobj.append(DigitalObject("iPhoneAppProgrammingGuide.pdf", "42409/pv60d063h", "pdf", "3", "29-Feb-2004"))
    myobj.append(DigitalObject("polite eating.jpg", "42409/sm508655g", "image/jpg", "1", "05-July-2003", "image2"))
    myobj.append(DigitalObject("ECM0906.pdf", "42409/f9178r251", "pdf", "7", "31-Oct-2003"))
    myobj.append(DigitalObject("question.jpg", "42409/0k35wv26k", "image/jpg", "3", "31-Mar-2002", "image4"))
    myobj.append(DigitalObject("9780271032689_09_CH04_p113-148.pdf", "42409/9177pv46w", "pdf", "10", "18-Aug-2001"))

    
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

def handle_uploaded_file(udir, f):
    fname = os.path.join(udir, f.name)
    print "saving %s" % fname
    destination = open(fname, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def upload_object(request):
    if request.method == 'POST':
        
        ark = identity.mint_new()
        print "posting:%s" % ark
        
        uploaddir = mkdtemp()
        print "dir:%s" % uploaddir

        # loop over the files to upload
        for i in range(int(request.POST.get('upload_count'))):
            f = request.FILES['file_'+str(i+1)]
            print "file:%s" % f 
            handle_uploaded_file(uploaddir, f)

        # done uploading the files 

        repopath = storage.ingest_directory(ark, uploaddir)
        identity.bind(ark, repopath, 'dmc186')

        # loop over metadata to store
        for i in range(int(request.POST.get('metadata_count'))):
            k = request.POST.get('meta_type_'+str(i+1))
            v = request.POST.get('meta_value_'+str(i+1))
            print "%s %s=>%s" % (ark, k, v)
            annotation = (ark, ("dc", "http://purl.org/dc/elements/1.1/", k), v) 
            annotate.add(ark, annotation)
       
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
