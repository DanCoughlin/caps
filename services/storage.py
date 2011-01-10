import os
import pairtree
import bagit
import git
#from tasks import store as store_task


tree_location = "/dlt/caps/datastore/stewardship"

def add(identifier, source):
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

    repo = git.Repo.init(pairobj.location)    
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

def get_or_create_file(identifier, f):
    # identifier should look like 42409/1f39k0594
    store = pairtree.PairtreeStorageClient(store_dir=tree_location, uri_base="ark://")
    if not store.exists(identifier):
        raise pairtree.ObjectNotFoundException("Object not found in pairtree: %s" % identifier)
    if store.exists(identifier, path=os.path.join("obj", f)):
        # return the file as a string
        return store.get_stream(identifier, path='obj', stream_name=f)
    else:
        # create an empty file and return None
        store.put_stream(identifier, path='obj', stream_name=f, bytestream='')
        return None
        
def put_file(identifier, f, bytestream):
    # the versioning stuff in here should probably be pulled into its own set
    #   of functions, or at least consolidated within the function
    store = pairtree.PairtreeStorageClient(store_dir=tree_location, uri_base="ark://")
    if not store.exists(identifier):
        raise pairtree.ObjectNotFoundException("Object not found in pairtree: %s" % identifier)
    if store.exists(identifier, path=os.path.join("obj", f)):
        obj = pairtree.PairtreeStorageObject(identifier, store)
        objroot = os.path.join(obj.id_to_dirpath(), "obj")
        # file already in pairtree, so:
        #   0. Make sure under version control
        try:
            repo = Repo(objroot)
        except git.InvalidGitRepositoryError:
            repo = git.Repo.init(objroot)
        #   1. commit if latest is uncommitted
        index = repo.index
        if repo.is_dirty():
            # right thing to do here?
            index.commit("repo is dirty within put_file")
        if f in repo.untracked_files:
            index.add([f])
            index.commit("within put_file, file %s had uncommitted changes" % f)
        #   2. overwrite the file
        store.put_stream(identifier, path='obj', stream_name=f, bytestream=bytestream)
        #   3. commit
        index = repo.index
        index.add([f])
        index.commit("updated file %s via put_file" % f)
    else:
        store.put_stream(identifier, path='obj', stream_name=f, bytestream=bytestream)
        # add to version control
        # commit
    return True
