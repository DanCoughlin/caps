import os
import pairtree
import bagit
from git import Repo
from celery.decorators import task

@task
def add(tree_location, identifier, source):
    # make_bag takes a directory for an argument
    print source
    bag = bagit.make_bag(source, processes=0)
    print bag.path
    #if not bag.validate():
    #    print "bag not valid"
    #    return None  
    f = pairtree.PairtreeStorageFactory()
    pairstore = f.get_store(store_dir=tree_location, uri_base="ark://")
    pairobj = pairstore.create_object(identifier)
    pairobj.add_directory(bag.path)
    print pairobj.location
    # nasty workaround since git commit requires terminal login
    # and os.getlogin() causes ioctl error
    import pwd
    os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

    repo = Repo.init(pairobj.location)    
    # files are loaded relative to the repository, so this 
    # prefix gets to the root of the filesystem as the repo
    # currently sits in repo_path/
    index = repo.index
    # make a copy of untracked files for logging purposes 
    # (otherwise they are no longer 'untracked' after added to index
    untracked = repo.untracked_files
    print untracked
    index.add(repo.untracked_files)
    c = index.commit("initializing this repo:%s" % untracked)
    print c
    return pairobj.location
