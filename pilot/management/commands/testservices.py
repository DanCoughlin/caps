import shutil
from tempfile import mkdtemp
from django.core.management.base import BaseCommand
from services import identity, fixity, storage, annotate


class Command(BaseCommand):
    args = '<file>'
    help = 'test basic services'

    def handle(self, *args, **options):
        print "starting"
        source_location = mkdtemp()
        myfile = args[0]
        shutil.copy(myfile, source_location)
        new_id = identity.mint()
        print "new_id:%s" % new_id
        print "exists:%s" % identity.exists(new_id)
        print "is it valid:%s" % identity.validate(new_id)

        identity.bind(new_id, myfile, 'tstem31')

        print "exists:%s" % identity.exists(new_id)
        print "store"
        storage.ingest_directory(new_id, source_location)
        print "stored"

        fix = fixity.generate(myfile, 'md5')
        print "fixity for %s is: %s" % (myfile, fix)
        fixity.bind(new_id, fix)

        print "adding an annotation"
        assertions = []
        assertions.append((new_id, ("dc", "http://purl.org/dc/elements/1.1/", "title"), "this is a test title"))
        assertions.append((new_id, ("dc", "http://purl.org/dc/elements/1.1/", "author"), "Shakespeare, Billy"))
        annotate.add(new_id, assertions)
        print "annotation added"
        print "ending"
        return 

"""
def store_it(ark_id):
    # make_bag takes a directory for an argument
    bag = bagit.make_bag("/tmp/testbag")
    if not bag.validate():
        print "bag not valid"
        sys.exit(1)
    print bag.path
    location = storage.add("/dlt/caps/datastore", ark_id, bag.path)
    return location
"""	
"""
this function should add a file to a repo
"""
"""
def add(f):
    repo_path = "/dlt/users/dmc186/caps-gitrepo"
    repo = git.Repo(repo_path)
    # files are loaded relative to the repository, so this 
    # prefix gets to the root of the filesystem as the repo
    # currently sits in repo_path/
    index = repo.index
    index.add([f])
    print "think we is there"
    index.commit("from the python program")
    return
"""
"""
if __name__ == "__main__":
    sys.exit(main())
"""
