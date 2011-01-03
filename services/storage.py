import os
import pairtree
import bagit
from git import Repo
#from tasks import store as store_task

def store(identifier, source):
    tree_location = "/dlt/caps/datastore/stewardship"
    #s = store_task.add.delay(tree_location=tree_location,
    #                         identifier=identifier,
    #                         source=source)
    #return s.get()

    # make_bag takes a directory for an argument
    bag = bagit.make_bag(source, processes=0)
    f = pairtree.PairtreeStorageFactory()
    pairstore = f.get_store(store_dir=tree_location, uri_base="ark://")
    pairobj = pairstore.create_object(identifier)
    pairobj.add_directory(bag.path)
    
    # nasty workaround since git commit requires terminal login
    # and os.getlogin() causes ioctl error
    #celery workaround - import pwd
    #celery workaround - os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

    repo = Repo.init(pairobj.location)    
    # files are loaded relative to the repository, so this 
    # prefix gets to the root of the filesystem as the repo
    # currently sits in repo_path/
    index = repo.index
    # make a copy of untracked files for logging purposes 
    # (otherwise they are no longer 'untracked' after added to index
    untracked = repo.untracked_files

    index.add(repo.untracked_files)
    c = index.commit("initializing this repo:%s" % untracked)

    return pairobj.location
