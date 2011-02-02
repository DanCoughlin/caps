import pairtree
import bagit
import git
from caps.services import settings, identity
#import subprocess
#from twisted.internet import defer
#from tasks import store as store_task



def create_store(path, uri=settings.URI_BASE):
    return pairtree.PairtreeStorageClient(store_dir=path, uri_base=uri)

def get_store(identifier, location=None):
    if location:
        tree_location = location
    else:
        tree_location = settings.TREE_LOCATION
    store = pairtree.PairtreeStorageClient(store_dir=tree_location,
                                           uri_base=settings.URI_BASE)
    identifier = identity.remove_scheme(identifier)
    if not store.exists(identifier):
        raise pairtree.ObjectNotFoundException(
            "Object not found in pairtree: %s" % identifier)
    return store

def ingest_directory(identifier, source, override_tree_location=None):
    #s = store_task.add.delay(tree_location=tree_location,
    #                         identifier=identifier,
    #                         source=source)
    #return s.get()

    # make_bag takes a directory for an argument
    bag = bagit.make_bag(source)
    pairstore = get_store(identifier, override_tree_location)
    pairobj = pairstore.create_object(identifier)
    pairobj.add_directory(bag.path)
    
    # nasty workaround since git commit requires terminal login
    # and os.getlogin() causes ioctl error
    #celery workaround - import pwd
    #celery workaround - os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]
   
    repo = init_version(pairobj.location)
    (index, untracked) = stage_all(repo)
    commit_version(index, "initializing repo with: %s" % untracked)

    # TODO: get this working
    # characterize the object (not working synchronously
    #   (due to jhove2 subproc?))
    #deferred = characterize(pairobj.location)
    #deferred.addCallback(add_to_version_control, repo)

    return pairobj.location

def commit_version(index, message=''):
    if not message:
        message = 'message not specified'
    c = index.commit(message)
    # you might expect the index to be empty after a commit but there's
    # a bug in gitpython.  doing this manually for now.  have notified
    # the gitpython devs, and patched our installation.
    index.update()
    return c

def stage_file(repo, f):
    index = repo.index
    index.add([f])
    return index

def stage_all(repo):
    index = repo.index
    # make a copy of untracked files for logging purposes 
    # (otherwise they are no longer 'untracked' after added to index)
    untracked = repo.untracked_files
    index.add(repo.untracked_files)
    index.add([diff.a_blob.name for diff in index.diff(None)])
    return (index, untracked)

def checkout_file(repo, f, commit_id):
    return repo.git.checkout(commit_id, f)
    
def init_version(directory):
    # pass in a directory, return a git.Repo
    # note that init() is a safe operation, won't break an existing repo
    return git.Repo.init(directory)

def get_or_create_file(identifier, f):
    # identifier should look like 42409/1f39k0594
    try:
        return get_file(identifier, f)
    except pairtree.FileNotFoundException:
        # create an empty file
        return put_file(identifier, f, bytestream='')

def get_file(identifier, f):
    # identifier should look like 42409/1f39k0594
    store = get_store(identifier)
    if store.exists(identifier, path=f):
        # return the file as a string
        return store.get_stream(identifier, path='', stream_name=f)
    else:
        raise pairtree.FileNotFoundException("File not found: %s" % f)

def list_versions(identifier, f=None):
    store = get_store(identifier)
    obj = pairtree.PairtreeStorageObject(identifier, store)
    repo = git.Repo(obj.id_to_dirpath())
    return _list_versions(repo, f)

def _list_versions(repo, f=None):
    if f:
        log_entries = repo.git.log("--pretty=oneline", f).split("\n")
    else:
        log_entries = repo.git.log("--pretty=oneline").split("\n")
    versions = []
    for entry in log_entries:
        split = entry.split()
        commit = split[0]
        message = u' '.join(split[1:])
        versions.append({commit: message})
    return versions

def remove_versioned_file(repo, f, message=''):
    repo.git.rm(f)
    index = repo.index
    c = commit_version(index, message)
    return c

def remove_file(identifier, f):
    store = get_store(identifier)
    assert store.exists(identifier, path=f), "File not found: %s" % f
    obj = pairtree.PairtreeStorageObject(identifier, store)
    remove_versioned_file(git.Repo(obj.id_to_dirpath()), f)
    return None

def rename_versioned_file(repo, f, f2, message=''):
    repo.git.mv(f, f2)
    index = repo.index
    c = commit_version(index, message)
    return c

def rename_file(identifier, f, f2):
    store = get_store(identifier)
    assert store.exists(identifier, path=f), "File not found: %s" % f
    obj = pairtree.PairtreeStorageObject(identifier, store)
    rename_versioned_file(git.Repo(obj.id_to_dirpath()), f, f2)
    return None

def put_file(identifier, f, bytestream):
    # the versioning stuff in here should probably be pulled into its own set
    #   of functions
    store = get_store(identifier)
    obj = pairtree.PairtreeStorageObject(identifier, store)
    objroot = obj.id_to_dirpath()
    # make sure under version control
    repo = init_version(objroot)
    # write the file
    store.put_stream(identifier, path='', stream_name=f, bytestream=bytestream)
    # stage and commit to version repo
    (index, untracked) = stage_all(repo)
    commit_version(index, "updated file %s via put_file" % f)
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
