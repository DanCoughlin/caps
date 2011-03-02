import rdflib
import StringIO
import os
import git
from contextlib import contextmanager
from caps.services import storage, identity
from caps.pilot.models import RDFMask, Philes


class Annotation(object):
    """
    what is an annotation?

    agent A asserts statement S about object O at datetime D
      where statement S has a property P and value V
      and value V possibly has type T and language L

    """
    # an annotation for now is a tuple of length 3 like follows:
    #   (subject, property, value) where:
    #   * subject is ark:/42409/foobarid
    #   * property is (dc, http://purl.org/dc/terms/, title)
    #     i.e., (label, vocab uri, element)
    #   * value is "Hamlet"
    pass


def add(identifier, annotation):
    # parse id (allow annotations of an ARK or part of an ARK)
    #   push this off till next phase and require all assertions
    #   to be at the object rather than file level
    pass

    # make sure id exists
    if not identity.exists(identifier):
        return False

    annotations = storage.get_or_create_file(identifier, "about.nt")
    # get_or_create annotations file from storage
    #   hardcode this filename to about.ttl?
# block out b.c. RDF lib was to sloooow
#    #annotations = storage.get_or_create_file(identifier, "about.n3")
#
#    # instantiate a graph
#    g = rdflib.ConjunctiveGraph()
#
#    if annotations:
#        # pull existing annotations into in-memory rdf graph
#        g.parse(StringIO.StringIO(annotations), format="n3")
#
#    # assume client sends list of strings/tuples (KLUDGE)
#    for assertion in annotation:
#        ns = rdflib.Namespace(assertion[1][1])
#        ns_label = assertion[1][0]
#        triple = (rdflib.URIRef(assertion[0]),
#                  ns[assertion[1][2]],
#                  rdflib.Literal(assertion[2]))
#
#        # attach annotation to annotations file
#        g.bind(ns_label, ns)
#        g.add(triple)
#
#        # write annotation to central datastore
#        #   push this off till future iteration
#        __rdfstore_write(triple, ns_label, ns)
# temp filx until we get rdf store working better
    if not annotations: 
        annotations = ""
    for assertion in annotation:
        trip = '<%s> <%s> "%s" .\n' % (assertion[0], assertion[1], assertion[2])
        RDFMask().create_mask(assertion[0], os.path.basename(assertion[1]), assertion[2])
        annotations += trip

    # validate annotations (don't write garbage)
    #   maybe rdflib is doing this for us in g.parse & g.add?
    pass

    # write annotations file using storage service
    #   this should ask storage to up the repo version
    # storage.put_file(identifier, "about.n3", g.serialize(format="n3"))
    storage.put_file(identifier, "about.nt", annotations) 

    return True


"""
function will update the metadata key/value pair 
in the database for a given id in the database. 
Then pull out all the meta data and overwrite 
the existing triple file. Assuming it is easier to
overwrite that with new info the pick out the updated
info - we are only updating one key/value at a time
"""
def update(db_id, key, val):
    # update database
    mask = RDFMask().update_triple(db_id, key, val) 
    new_annotation_file(mask.phile)


"""
removes a metadata element and updates the triple 
file
"""
def remove(db_id):
    #update db
    r = RDFMask.objects.filter(pk=db_id)
    p = Philes.objects.filter(identifier=r[0].phile.identifier)
    RDFMask().remove_mask(db_id)
    new_annotation_file(p)


"""
creates a new about.nt file for the existing triples in the database
"""
def new_annotation_file(p):
    # create a new set of annotations to store in about.nt
    trips = RDFMask.objects.filter(phile=p)
    annotations = ""
    for t in trips:
        x = '<%s> <%s> "%s" .\n' % (t.phile.identifier, t.triple_predicate, t.triple_object)
        annotations += x

    # overwrite existing about.nt with new triples
    # put_file, will update git
    storage.put_file(trips[0].phile.identifier, "about.nt", annotations)

    #repo = git.Repo(trips[0].phile.path)
    #storage.commit_version(repo.index, "updated metadata " + key + "=>" + val)
    return True



def query(q):
    """
    q should be a SPARQL query such as:

    SELECT ?title
    WHERE { ?subj <http://purl.org/dc/elements/1.1/title> ?title }

    which grabs all titles from any subject containing the dc:title pred.

    returns a list of hits
    """
    rdflib.plugin.register(
        'sparql', rdflib.query.Processor,
        'rdfextras.sparql.processor', 'Processor')
    rdflib.plugin.register(
        'sparql', rdflib.query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')
    with open_rdfstore() as graph:
        query_resp = graph.query(q)
    return query_resp.result

@contextmanager
def open_rdfstore(configString="/var/data/rdfstore.bdb", identifier=""):
    store = rdflib.plugin.get('Sleepycat', rdflib.store.Store)('rdfstore')
    graph = rdflib.ConjunctiveGraph(store='Sleepycat',
                                    identifier=identifier)
    try:
        rt = graph.open(configString, create=False)
        assert rt != rdflib.store.NO_STORE, "RDFstore is empty"
        assert rt == rdflib.store.VALID_STORE
        yield graph
    finally:
        graph.close()

def __rdfstore_write(triple, ns_label, ns):
    with open_rdfstore() as graph:
        graph.bind(ns_label, ns)
        graph.add(triple)
        graph.commit()
    return

def __dump_all():
    with open_rdfstore() as graph:
        n3 =  graph.serialize(format="n3")
    return n3

