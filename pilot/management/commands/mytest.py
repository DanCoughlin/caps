from django.core.management.base import BaseCommand
from services import identity, fixity, storage


class Command(BaseCommand):
    args = ''
    help = 'test basic identity, fixity, and storage'

    def handle(self, *args, **options):
        print "starting"
        myfile = "/dlt/users/dmc186/dltmap.js"
        bag_location = "/tmp/testbag"
        new_id = identity.mint()
        print "new_id:%s" % new_id
        print "exists:%s" % identity.exists(new_id)
        print "is it valid:%s" % identity.validate(new_id)

        identity.bind(new_id, myfile)

        print "exists:%s" % identity.exists(new_id)
        print "store"
        storage.store(new_id, bag_location)
        print "stored"

        fix = fixity.generate(myfile, 'md5')
        print "fixity for %s is: %s" % (myfile, fix)
        print "fixity exists? %s" % fixity.exists(fix)
        fixity.bind(new_id, fix)
        print "fixity exists? %s" % fixity.exists(fix)

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
    location = storage.store("/dlt/caps/datastore", ark_id, bag.path)
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
