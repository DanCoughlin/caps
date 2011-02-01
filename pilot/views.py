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
    label = 'Upload New Batch'
    if type == 'object':
        batch = False
        label = 'Upload New Object'
    meta_values = ['select meta type', 'contributor', 'coverage', 
        'creator', 'date', 'description', 'format', 'identifier', 
        'language', 'publisher', 'relation', 'rights', 'source', 
        'subject', 'title', 'type']
    
    return render_to_response('ingest.html', {'meta': meta_values, 'batch': batch, 'label': label});


def handle_file_upload(udir, f):
    fname = os.path.join(udir, f.name)
    print "saving %s" % fname
    destination = open(fname, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return fname


""" 
handles unpacking many archive types from
the is_archive function
afile is the location of the archived file
atype is the type of file from the content_type
    passed via form
"""
def unpack_archive(afile_name, fil):
    atype = fil.content_type
    tmp_pth = os.path.dirname(afile_name)
    print "path:%s" % tmp_pth

    suffix = atype.split("/")    
    if len(suffix) != 2:
        return False
    
    if suffix[1] == 'zip':  
        print "zip"
        af = zipfile.ZipFile(afile_name, "r")
    elif suffix[1] == 'x-tar':
        print "tar"
        af = tarfile.open(afile_name, "r")
    elif suffix[1] == 'x-gzip':
        print "gzip"
        af = tarfile.open(afile_name, "r:gz")
    elif suffix[1] == 'x-bzip2':
        print "bzip2"
        af = tarfile.open(afile_name, "r:bz2")
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


"""
determines if the file being uploaded is an archived file to unpack
"""
def is_archive(uploadfile):
    archive_types = ['application/x-gzip', 'application/x-tar', 'application/zip', 
        'application/x-bzip2']
    return uploadfile.content_type in archive_types


"""
determines if the file being uploaded is an spreadsheet 
"""
def is_spreadsheet(uploadfile):
    spreadsheet_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    return uploadfile.content_type in spreadsheet_types     


def get_meta_dict(spreadsheet):
   # make sure filename is set to xls file
   #book = xlrd.open_workbook('/Users/dmc186/test.xls')
   book = xlrd.open_workbook(spreadsheet)
   # grab first sheet of xls
   sheet = book.sheet_by_index(0)
   # first row of sheet = column headings/metadata elements
   headings = sheet.row(0)
   # the reason for this dict and for loop is to make order of headings not matter
   fields = {}
   fields['title'] = []
   fields['creator'] = []
   fields['date'] = []
   fields['coverage'] = []
   fields['description'] = []
   fields['type'] = []
   fields['subject'] = []
   fields['source'] = []
   fields['format'] = []
   fields['rights'] = []
   fields['relation'] = []
   fields['identifier'] = []
   fields['contributor'] = []
   fields['publisher'] = []

   for i, field in enumerate(headings):
      field.value = field.value.strip()
      # where 'Title' is a heading from the xls
      if field.value == 'Filename':
         fields['filename'] = i 
      elif field.value == 'Creator':
         fields['creator'].append(i)
      elif field.value == 'Creator 2':
         fields['creator'].append(i)
      elif field.value == 'Title':
         fields['title'].append(i)
      elif field.value == 'Title/View':
         fields['title'].append(i)
      elif field.value == 'Other title':
         fields['title'].append(i)
      elif field.value == 'Date':
         fields['date'].append(i)
      elif field.value == 'Earliest date':
         fields['date'].append(i)
      elif field.value == 'Latest date':
         fields['date'].append(i)
      elif field.value == 'Date Photographed':
         fields['date'].append(i)
      elif field.value == 'Current Location':
         fields['coverage'].append(i)
      elif field.value == 'Discovery location':
         fields['coverage'].append(i)
      elif field.value == 'Former location':
         fields['coverage'].append(i)
      elif field.value == 'Description of work':
         fields['description'].append(i)
      elif field.value == 'Description of view':
         fields['description'].append(i)
      elif field.value == 'Inscription':
         fields['description'].append(i)
      elif field.value == 'Work Type':
         fields['type'].append(i)
      elif field.value == 'Style of work':
         fields['type'].append(i)
      elif field.value == 'Resource type':
         fields['type'].append(i)
      elif field.value == 'Culture':
         fields['subject'].append(i)
      elif field.value == 'Subject of work':
         fields['subject'].append(i)
      elif field.value == 'Source':
         fields['source'].append(i)
      elif field.value == 'File format':
         fields['format'].append(i)
      elif field.value == 'Image size':
         fields['format'].append(i)
      elif field.value == 'Permitted uses':
         fields['rights'].append(i)
      elif field.value == 'Public/Private':
         fields['rights'].append(i)
      elif field.value == 'Collection':
         fields['relation'].append(i)
      elif field.value == 'Sub collection':
         fields['relation'].append(i)
      elif field.value == 'Record ID':
         fields['identifier'].append(i)
      elif field.value == 'Cataloger':
         fields['contributor'].append(i)
      elif field.value == 'Copyright Holder':
         fields['publisher'].append(i)
      else:
         pass

    return fields


"""
handles the batch upload format which enforces a spreadsheet of metadata
in the first file and an archive as the second file upload
the spreadsheet contains metadata fields, one which will be the 
file names to associate the row of metadata with the file to uplaod
        file_0 is metadata spreadsheet
        file_1 is zip file for uploads
        verify - file_0 is valid spreadsheet
        verify - file_1 is valid archive
"""
def upload_batch(request):
    if request.method == 'POST':
        spreadsheet = request.FILES['file_0']
        archive = request.FILES['file_1']

        # enforce the upload files order/type
        if not is_spreadsheet(spreadsheet) or not is_archive(archive):
            print "one of your files just ain't right"
            return render_to_response('ingest.html', {'batch': True});

        # both uploads are valid: process batch upload
        # upload spreadsheet and pass file to get_meta_dict
        uploaddir = mkdtemp()
        ss = handle_file_upload(uploaddir, spreadsheet) 

        # loop over spreadsheet and create metadata
        # dictionary
        metadict = get_meta_dict(ss)

        # unpack the archive file, 
        aname = os.path.join(uploaddir, archive.name)
        unpack_archive(aname, archive)

        # create identifier for each object
        # upload object individually and assign
        # -------  loop over the metadata dict and find file name
        # -------  and then upload that file that I unpacked and associate
        # -------  that row of meta data
        # the metadata dictionary to object 

 

"""
function takes a request from the ingest screen
and determines what actions to take for upload
"""
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
    
            # archive file and user has selected to have system unpack
            if request.POST.has_key(cb_key) == False and is_archive(f):
                print "unpack"
                aname = os.path.join(uploaddir, f.name)
                unpack_archive(aname, f)
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


"""
return screen to view object management
"""
def management(request, arkid):
    return render_to_response('management.html', {'arkid': arkid})


"""
display screen shots for stake holders
to provide feedback
"""
def screenshots(request):
    return render_to_response('screenshots.html');
