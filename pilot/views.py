import datetime
import logging
import mimetypes
import os.path
import zipfile
import tarfile
import re
import string
import xlrd
import shutil
import sys
import settings
import pairtree
import magic
from urllib import unquote
from services import identity, storage, annotate 
from models import Philes, RDFMask, Audit, Log
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
from stat import * 
from django.contrib.auth.decorators import login_required 

@login_required
def default(request, display='icons'):
    phils = Philes.objects.filter(owner='dmc186')
    stats = Philes().get_stats()
    myobj = []
#movie: <img src="/site_images/icon_movie_48.png" alt="movie file" />
#zip: <img src="/site_images/icon_zip_48.png" alt="zip file" />
    for p in phils:
        
        metadata = RDFMask.objects.filter(phile=p)
        version = len(storage.list_versions(p.identifier))
        title = RDFMask().get_title(p) 
        # if we don't have the object type then default to compound
        if settings.ICONS.has_key(p.obj_type):
            myobj.append(DigitalObject(title, p.identifier, p.obj_type, version, p.date_updated, settings.ICONS[p.obj_type][0], settings.ICONS[p.obj_type][1])) 
        else:
            myobj.append(DigitalObject(title, p.identifier, p.obj_type, version, p.date_updated, settings.ICONS["default"][0], settings.ICONS["default"][1])) 

    if display == 'icons':
        return render_to_response('icons.html', {'objects': myobj, 'stats': stats})
    else: 
        return render_to_response('list.html', {'objects': myobj, 'stats': stats})


def get_identifier(request):
    id = identity.mint()

    if (identity.validate(id) ):
        return render_to_response('identifier.html', {'identifier' : id })
    else:
        return render_to_response('identifier.html', {'identifier' : "0" })        


"""
display form to upload a new object or batch upload
"""
@login_required
def new_object(request, type):
    stats = Philes().get_stats()
    if type == 'object':
        return render_to_response('ingest.html', {'meta': sorted(settings.METADATA_URLS.keys()), 'stats': stats})
    else:
        return render_to_response('ingest_batch.html', {'meta': sorted(settings.METADATA_URLS.keys()), 'stats': stats})


"""
returns a data dictionary mapping of the spreadsheet to our dc elements
for batch upload
"""
def get_meta_dict(spreadsheet):
    # make sure filename is set to xls file
    #book = xlrd.open_workbook('/Users/dmc186/test.xls')
    book = xlrd.open_workbook(spreadsheet)
    # grab first sheet of xls
    sheet = book.sheet_by_index(0)
    # first row of sheet = column headings/metadata elements
    headings = sheet.row(0)
    # the reason for this dict and for loop is to make order of headings not matter
    fields = dict(filename='', title=[], creator=[], date=[], coverage=[],
                  description=[], type=[], subject=[], source=[],
                  format=[], rights=[], collection=[], identifier=[],
                  contributor=[], publisher=[])

    for i, field in enumerate(headings):
        field.value = field.value.strip()

        if field.value == 'Filename':
            fields['filename'] = i
        elif field.value in ('Creator', 'Creator 2',):
            fields['creator'].append(i)
        elif field.value in ('Title', 'Title/View', 'Other title',):
            fields['title'].append(i)
        elif field.value in ('Date', 'Earliest date', 'Latest date',
                             'Date Photographed',):
            fields['date'].append(i)
        elif field.value in ('Current Location', 'Discovery location',
                             'Former location',):
            fields['coverage'].append(i)
        elif field.value in ('Description of work', 'Description of view',
                           'Inscription',):
            fields['description'].append(i)
        elif field.value in ('Work Type', 'Style of work', 'Resource type',):
            fields['type'].append(i)
        elif field.value in ('Culture', 'Subject of work',):
            fields['subject'].append(i)
        elif field.value in ('Source',):
            fields['source'].append(i)
        elif field.value in ('File format', 'Image size',):
            fields['format'].append(i)
        elif field.value in ('Permitted uses', 'Public/Private',):
            fields['rights'].append(i)
        elif field.value in ('Collection', 'Sub collection',):
            fields['collection'].append(i)
        elif field.value in ('Record ID',):
            fields['identifier'].append(i)
        elif field.value in ('Cataloger',):
            fields['contributor'].append(i)
        elif field.value in ('Copyright Holder',):
            fields['publisher'].append(i)
        else:
            pass

    metadata = {}

    # loop over the rows in the spreadsheet and create
    # a data dict for each row where the filename is 
    # the key 
    #  the metadata dictionary is a dictionary of dictionaries
    # where the key is the filename and the value of that dict 
    # is dictionary of metatdata elements with a list of the values
    # for that element as the "value"
    for row_num in range(1, sheet.nrows):
        # don't add the headings
        if not row_num == 0:
            row = sheet.row(row_num)
            fn = row[fields['filename']].value
            # key for each row is the filename to key on the zip file
            metadata[fn] = {}
            dcfields = settings.METADATA_URLS.keys()

            # loop over the fields and create more dicts of lists                 
            # key is one of the dcfields and the value is a list of that
            # metadatas values from the spreadsheet
            for i in dcfields:
                metadata[fn][i] = []
                # loop over mapped elements
                for j in fields[i]:
                    if not row[j].value == "":
                        # append the value from the spreadsheet to the list
                        metadata[fn][i].append(row[j].value)
    return metadata 


"""
determines if the file being uploaded is an archived file to unpack
"""
def is_archive(uploadfile):
    print "archive type: %s" % uploadfile.content_type
    if is_zip(uploadfile) or is_tar(uploadfile) or is_bzip(uploadfile) or is_gzip(uploadfile):
        return True
    else:
        return False
    

"""
series of functions for checking archive type
"""
def is_zip(uploadfile):
    archive_types = ['application/zip', 'application/x-zip-compressed']
    return uploadfile.content_type in archive_types

def is_tar(uploadfile):
    archive_types = ['application/x-tar']
    return uploadfile.content_type in archive_types

def is_bzip(uploadfile):
    archive_types = ['application/x-bzip2']
    return uploadfile.content_type in archive_types

def is_gzip(uploadfile):
    archive_types = ['application/x-gzip']
    return uploadfile.content_type in archive_types


"""
determines if the file being uploaded is an spreadsheet 
"""
def is_spreadsheet(uploadfile):
    spreadsheet_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    print "spreadsheet type: %s" % uploadfile.content_type
    return uploadfile.content_type in spreadsheet_types     


"""
upload a single file to a temp directory
"""
def handle_file_upload(udir, f):
    fname = os.path.join(udir, f.name)
    print "saving %s" % fname
    with open(fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return fname


""" 
handles unpacking many archive types from
the is_archive function
afile is the location of the archived file
atype is the type of file from the content_type
    passed via form
"""
def unpack_archive(afile_name, fil):

    tmp_path = os.path.dirname(afile_name)

    if is_zip(fil):
        af = zipfile.ZipFile(afile_name, "r")
    elif is_tar(fil):
        af = tarfile.open(afile_name, "r")
    elif is_gzip(fil):
        af = tarfile.open(afile_name, "r:gz")
    elif is_bzip(fil):
        af = tarfile.open(afile_name, "r:bz2")
    else:
        print "no match for archive: %s" % afile_name 
        return False

    # Sanitize - ensure no absolute paths or '../' 
    #if suffix[1] == 'zip' or suffix[1] == 'x-zip-compressed':  
    if is_zip(fil): 
        for name in af.namelist():
            if os.path.isabs(name) or re.match('^\.\.', name):
                print "file no good: %s" % name
                return False
    # Sanitize for all non zip archives
    else:
        for f in af:
            if os.path.isabs(f.name) or re.match('^\.\.', f.name):
                print "file no good: %s" % f.name
                return False
    print "extracting archive: %s" % tmp_path
    af.extractall(tmp_path)
    af.close()
    # we don't store the actual archived file 
    print "remove the actual zip file - don't store that:%s" % afile_name
    os.remove(os.path.join(tmp_path, afile_name))

    # mac adds this __MACOSX directory to archive files, don't add it to the bag 
    annoying_mac_dir = os.path.join(tmp_path, "__MACOSX")  
    if os.path.exists(annoying_mac_dir):
        print "remove that mac zip file, don't archive: %s" % annoying_mac_dir
        shutil.rmtree(annoying_mac_dir)


"""
handles the batch upload format which enforces a spreadsheet of metadata
in the first file and an archive as the second file upload
the spreadsheet contains metadata fields, one which will be the 
file names to associate the row of metadata with the file to uplaod
        file_0 is zip file for uploads
        file_1 is metadata spreadsheet
        verify - file_0 is valid spreadsheet
        verify - file_1 is valid archive
"""
@login_required
def upload_batch(request):
    if request.method == 'POST':
        archive = request.FILES['file_0']
        spreadsheet = request.FILES['file_1']
        stats = Philes().get_stats()

        # enforce the upload files order/type
        if not is_spreadsheet(spreadsheet):
            print "spreadsheet file just ain't right"
            return render_to_response('ingest_batch.html', {'batch': True, 'stats':stats})
        
        if not is_archive(archive):
            print "archive file just ain't right"
            return render_to_response('ingest_batch.html', {'batch': True, 'stats':stats})

        # both uploads are valid: process batch upload
        # upload spreadsheet and pass file to get_meta_dict
        uploaddir = mkdtemp()
        ss = handle_file_upload(uploaddir, spreadsheet) 

        # get spreadsheet meta data  
        metadict = get_meta_dict(ss)

        # unpack the archive file, 
        handle_file_upload(uploaddir, archive) 
        aname = os.path.join(uploaddir, archive.name)
        unpack_archive(aname, archive)

        # create identifier for each object
        # upload object individually and assign
        # -------  loop over the metadata dict and find file name
        errors = []
        for key,val in metadict.iteritems():
            fp = os.path.dirname(aname) + "/" + key
            # move the file from the zip into new tmp directory
            t = mkdtemp()
            sz = os.path.getsize(fp)
            mime = magic.Magic(mime=True)
            o_type = mime.from_file(fp) 
            shutil.move(fp, t) 
            newf = t + "/" + key
            try:
                
                ark = identity.mint_new()
                repopath = storage.ingest_directory(ark, t)
                identity.bind(ark, repopath, 'dmc186', sz, 1, o_type)
                # can't put this in ingest_directory b.c.
                # bind hasn't been done yet.  yucky.
                Log().logark(ark, 'ObjectIngested')
                assertions = []
                # loop over metadata to store
                for i, v in enumerate(val):
                    #print "\t%s" % v
                    for vals in metadict[key][v]:
                        #print "\t\t%s" % vals
                        #assertion = (ark, ("dc", "http://purl.org/dc/elements/1.1/", v), vals) 
                        assertion = (ark, settings.METADATA_URLS[v], vals) 
                        assertions.append(assertion)
                annotate.add(ark, assertions)
                shutil.rmtree(t)
            except IOError as (errno, strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
                print "%s" % newf 
                pass
            except:
                print "Unexpected error:", sys.exc_info()[0]
                print "%s" % newf 
                raise
        # we can now remove whole temp dir now(incl. spreadsheet) 
        shutil.rmtree(uploaddir)
    return HttpResponseRedirect('/pilot/list')


 

"""
function takes a request from the ingest screen
and determines what actions to take for upload
"""
@login_required
def upload_object(request):
    stats = Philes().get_stats()
    if request.method == 'POST':
             
        ark = identity.mint_new()
        print "posting:%s" % ark
        
        uploaddir = mkdtemp()
        print "dir:%s" % uploaddir

        # loop over the files to upload
        f_sz = 0
        f_nm = int(request.POST.get('upload_count', 1))
        o_type = ''
        for i in range(f_nm):
            f = request.FILES['file_'+str(i+1)]
            cb_key = 'unzip_cb_' + str(i+1)
            # if user does not want to unpack or just regular file upload
            print "index:%s" % str(i+1)
            print "file:%s" % f 
            print "filetype:%s" % f.content_type
            o_type = f.content_type
            # unpacking a file for user and uploading that
            f_sz += f.size
            print "size:%d" % f_sz
            handle_file_upload(uploaddir, f)
            # archive file and user has selected to have system unpack
            if request.POST.has_key(cb_key) == False and is_archive(f):
                print "unpack"
                aname = os.path.join(uploaddir, f.name)
                unpack_archive(aname, f)
                o_type = 'compound'
            print "------------\n"

        # done uploading the files 
        repopath = storage.ingest_directory(ark, uploaddir)
        print "num:%d totalsize:%d" % (f_nm, f_sz)
        if f_nm > 1:
            o_type = 'compound'
        identity.bind(ark, repopath, 'dmc186', f_sz, f_nm, o_type) 

        # can't be put in storage.ingest_directory because
        # bind hasn't happened yet - yucky.
        Log().logark(ark, 'ObjectIngested')
        add_assertions(request, ark)

        # remove temp files from webserver
        shutil.rmtree(uploaddir)

        # done adding metadata 
        return HttpResponseRedirect('/pilot/list')

    return render_to_response('ingest.html', {'batch': False, 'stats': stats})

"""
get the listing of versions for an object
"""
@login_required
def get_versions(request, arkid):
    versions = storage.list_versions(arkid)
    return render_to_response('versions.html', {'versions': versions, 'ark': arkid})

"""
remove a metadata element
"""
@login_required
def remove_metadata(request, metaid):
    annotate.remove(metaid) 
    return render_to_response('meta_delete.html', {'id': metaid})


"""
adds metadata to an existing object
"""
@login_required
def add_metadata(request):
    ark = request.POST.get('ark') 
    add_assertions(request, ark)

    p = Philes().get_phile(ark) 
    md = RDFMask().get_md(p) 
    versions = storage.list_versions(ark)
    return render_to_response('meta_new.html', {'phile': p, 'metadata': md, 'versions': versions, 'meta': sorted(settings.METADATA_URLS.keys()) })


"""
function to update the meta data for an object
"""
@login_required
def meta_update(request):
    m_id = request.POST.get('meta_id')
    m_type = request.POST.get('meta_type')
    m_value = request.POST.get('meta_value')
    annotate.update(m_id, m_type, m_value);

    triple = RDFMask.objects.get(pk=m_id)

    return render_to_response('meta.html', {'triple': triple} )


"""
function takes a request object and an arkid
and creates a new list of assertions/annotations
for that arkid object
"""
@login_required
def add_assertions(request, ark):
    assertions = []
    # loop over metadata to store
    for i in range(int(request.POST.get('metadata_count'))):
        k = request.POST.get('meta_type_'+str(i+1))
        v = request.POST.get('meta_value_'+str(i+1))
        #assertion = (ark, ("dc", "http://purl.org/dc/elements/1.1/", k), v) 
        #assertions.append(annotation)
        assertion = (ark, settings.METADATA_URLS[k], v) 
        assertions.append(assertion)
    annotate.add(ark, assertions)
       

# A view to report back on upload progress:
@login_required
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
@login_required
def management(request, arkid):
    stats = Philes().get_stats()
    p = Philes().get_phile(arkid)
    md = RDFMask().get_md(p)
    last_audit = Audit().get_last_audit(p)
    title = RDFMask().get_title(p)
    versions = storage.list_versions(arkid)
    path = p.path + "/data"
    img = "icon_folder"
    if settings.ICONS.has_key(p.obj_type):
        img = settings.ICONS[p.obj_type][0]

    for pth, drs, files in os.walk(path):
        pass
    return render_to_response('management.html', {'phile' : p, 'md' : md, 'files' : files, 'meta' : sorted(settings.METADATA_URLS.keys()), 'versions': versions, 'stats': stats, 'obj_name' : title, 'last_audit': last_audit, 'img': img})


"""
run audit on an object
"""
@login_required
def audit(request, arkid):
    a = storage.validate_object(arkid)
    return render_to_response('audit.html', {'audit':a})


"""
get log for an object
"""
@login_required
def get_log(request, arkid):
    print "identifier is %s" % arkid
    l = Log().get_log(arkid)
    return render_to_response('log.html', {'logs':l})

   

"""
runs search on metadata
"""
@login_required
def search(request, keyword):
    results = RDFMask().search(keyword)
    myobj = []
    id_tracker = ""
    o = None 
    print len(myobj)
    for r in results:
        
        if not r.phile.identifier == id_tracker:
            if not o == None: 
                myobj.append(o)
            title = RDFMask().get_title(r.phile)
            version = len(storage.list_versions(r.phile.identifier))
            if settings.ICONS.has_key(r.phile.obj_type):
                o = DigitalObject(title, r.phile.identifier, r.phile.obj_type, version, r.phile.date_updated, settings.ICONS[r.phile.obj_type][0], settings.ICONS[r.phile.obj_type][1], [])
            else:
                o = DigitalObject(title, r.phile.identifier, r.phile.obj_type, version, r.phile.date_updated, settings.ICONS["default"][0], settings.ICONS["default"][1], [])

        o.metadata.append( (r.triple_predicate, r.triple_object) ) 
        id_tracker = r.phile.identifier

    if not o == None:
        myobj.append(o)

    return render_to_response('search.html', {'keyword': keyword, 'obj': myobj})


"""
returns listing of matching metadata values for search autocomplete
"""
@login_required
def autocomplete(request):
    term = request.GET.get('term', '') 
    matches = RDFMask().get_autocomplete(term)    
    return render_to_response('autocomplete.html', {'matches': matches})


"""
function looks up the tree of files located
within a bag data/ directory.  this function
only returns one level of the tree at a time
"""
@login_required
def filetree(request):
    dir_id = request.POST.get("dir")
    dir_id = unquote(dir_id)
   
    # get the ark as everything leading up to /data
    a = dir_id.split("/data")
    ark = a[0]

    # payload dir is everything passed in dir beyond data
    payload = "/data/" + ''.join(a[1:]) 
    payload = os.path.normpath(payload)

    # get a pairtree client to get storage directory
    pairtree_client = storage.get_store(ark)
    obj = pairtree.PairtreeStorageObject(ark, pairtree_client)

    # directory where files/folders are
    data_path = obj.id_to_dirpath() + payload
    dirs = [] 
    files = [] 

    # loop over directory and store (separately) files from dirs
    # storing in a tuple b.c. the javascript requires it (what happened
    # to decoupling view/controller)
    for f in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, f)):
            dirs.append((os.path.join(dir_id, f), (f)))
        else:
            fullfile = os.path.join(dir_id, f)
            basename, ext = os.path.splitext(fullfile)
            ext = string.replace(ext, '.', '')
            #files.append((os.path.join(dir_id, f), (f), ext))
            files.append((fullfile, f, ext))
            
    return render_to_response('treeview.html', {'files':files, 'dirs': dirs })
