import os
import pairtree
import bagit
import git
import subprocess
from twisted.internet import defer
#from tasks import store as store_task


jhove2_path = "/usr/local/jhove2-0.6.0/jhove2.sh"
tree_location = "/dlt/caps/datastore/stewardship"
uri_base = "ark:/"

def create_store(path, uri=uri_base):
    return pairtree.PairtreeStorageClient(store_dir=path, uri_base=uri)

def add(identifier, source, override_tree_location=None):
    #s = store_task.add.delay(tree_location=tree_location,
    #                         identifier=identifier,
    #                         source=source)
    #return s.get()
    if override_tree_location:
        tree_location = override_tree_location

    # make_bag takes a directory for an argument
    bag = bagit.make_bag(source, processes=1)
    f = pairtree.PairtreeStorageFactory()
    pairstore = f.get_store(store_dir=tree_location, uri_base=uri_base)
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

    # TODO: get this working
    # characterize the object (not working synchronously (due to jhove2 subproc?))
    #deferred = characterize(pairobj.location)
    #deferred.addCallback(add_to_version_control, repo)

    return pairobj.location

add_object = add

# method was for attempt at async characterization invocation
#def add_to_version_control(f, repo):
#    print "f: %s" % f
#    print "repo: %s" % repo
#    index = repo.index
#    index.add([f])
#    index.commit("committing characs file asynchronously?")
#    return

def get_or_create_file(identifier, f):
    # identifier should look like 42409/1f39k0594
    store = pairtree.PairtreeStorageClient(store_dir=tree_location, uri_base=uri_base)
    if not store.exists(identifier):
        raise pairtree.ObjectNotFoundException("Object not found in pairtree: %s" % identifier)
    if store.exists(identifier, path=f):
        # return the file as a string
        return store.get_stream(identifier, path='', stream_name=f)
    else:
        # create an empty file and return None
        store.put_stream(identifier, path='', stream_name=f, bytestream='')
        return None
        
def put_file(identifier, f, bytestream):
    # the versioning stuff in here should probably be pulled into its own set
    #   of functions
    store = pairtree.PairtreeStorageClient(store_dir=tree_location, uri_base=uri_base)
    if not store.exists(identifier):
        raise pairtree.ObjectNotFoundException("Object not found in pairtree: %s" % identifier)
    #new_file = not store.exists(identifier, path=f)
    obj = pairtree.PairtreeStorageObject(identifier, store)
    objroot = obj.id_to_dirpath()
    # make sure under version control
    try:
        repo = git.Repo(objroot)
    except git.InvalidGitRepositoryError:
        repo = git.Repo.init(objroot)
    # commit if latest is uncommitted
    index = repo.index
    if repo.is_dirty():
        index.commit("(within put_file) repo is dirty")
    if f in repo.untracked_files:
        index.add([f])
        index.commit("(within put_file) file %s had uncommitted changes" % f)
    # write the file
    store.put_stream(identifier, path='', stream_name=f, bytestream=bytestream)
    # commit
    index = repo.index
    index.add([f])
    index.commit("updated file %s via put_file" % f)
    return True


"""
@defer.inlineCallbacks
def characterize(object_path):
    characs_file = os.path.join(object_path, "characterization.json")

    # run jhove2
    yield subprocess.Popen([
        jhove2_path,
        "-i",
        "-k",
        "-d",
        "JSON",
        "-o",
        characs_file,
        object_path])

    defer.returnValue(characs_file)
"""
