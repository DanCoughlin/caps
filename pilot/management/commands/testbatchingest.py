import shutil
import sys
import os
import zipfile
import tarfile
import magic
from tempfile import mkdtemp
from django.core.management.base import BaseCommand
from services import identity, fixity, storage, annotate
from pilot import views


class Command(BaseCommand):
    args = '<file>'
    help = 'test basic services'

    def handle(self, *args, **options):
        print "starting"
        if len(args) == 2:
            try:
                #spreadsheet = open(args[0], 'r')
                spreadsheet = args[0]
                archive = open(args[1], 'r')
            except IOError as (errno, strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
                print "Unable to open one of:\n%s\n%s" % (args[0], args[1])
                pass
        else: 
            #spreadsheet = open('/var/www/django/caps/pilot/tests/data/test-sm.xls', 'r')
            archive = open('/var/www/django/caps/pilot/tests/data/Archive-sm.zip', 'r')
            spreadsheet = '/var/www/django/caps/pilot/tests/data/test-sm.xls'
        
        uploaddir = mkdtemp()
        
        mime = magic.Magic(mime=True)
        atype = mime.from_file(archive.name)
        print "file type: %s" % atype
        suffix = atype.split("/")    
        if len(suffix) != 2:
            return False

        
        if suffix[1] == 'zip':  
            af = zipfile.ZipFile(archive.name, "r")
        elif suffix[1] == 'x-tar':
            af = tarfile.open(archive.name, "r")
        elif suffix[1] == 'x-gzip':
            af = tarfile.open(archive.name, "r:gz")
        elif suffix[1] == 'x-bzip2':
            af = tarfile.open(archive.name, "r:bz2")
        print "extracting archive: %s" % archive.name 
        af.extractall(uploaddir)
        af.close()
        print "extracted to:%s" % uploaddir
        # get spreadsheet meta data  
        metadict = views.get_meta_dict(spreadsheet)

        for key,val in metadict.iteritems():
            fp = uploaddir + "/" + key
            # move the file from the zip into new tmp directory
            t = mkdtemp()
            shutil.move(fp, t) 
            newf = t + "/" + key
            print "file:%s" % newf
            try:
                open(newf, "r")
                print "%s found" % newf 
                ark = identity.mint_new()
                repopath = storage.ingest_directory(ark, t)
                identity.bind(ark, repopath, 'dmc186')

                assertions = []
                # loop over metadata to store
                for i, v in enumerate(val):
                    #print "\t%s" % v
                    for vals in metadict[key][v]:
                        #print "\t\t%s" % vals
                        assertion = (ark, ("dc", "http://purl.org/dc/elements/1.1/", v), vals) 
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

        shutil.rmtree(uploaddir)
        print "ending"
        return 

