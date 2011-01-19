import rdflib
import StringIO
from datetime import datetime
from tempfile import mkdtemp
from contextlib import contextmanager
from caps.services import storage, identity


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

    # get_or_create annotations file from storage
    #   hardcode this filename to about.ttl?
    annotations = storage.get_or_create_file(identifier, "about.n3")
    print "identifier:%s" % identifier

    # instantiate a graph
    g = rdflib.ConjunctiveGraph()

    if annotations:
        # pull existing annotations into in-memory rdf graph
        g.parse(StringIO.StringIO(annotations), format="n3")

    print "graph:%s" % g.serialize(format="n3")
    print "annotation:%s" % list(annotation)

    # assume client sends strings/tuples (KLUDGE)
    ns = rdflib.Namespace(annotation[1][1])
    ns_label = annotation[1][0]
    triple = (rdflib.URIRef(annotation[0]),
              ns[annotation[1][2]],
              rdflib.Literal(annotation[2]))

    # attach annotation to annotations file
    g.bind(ns_label, ns)
    print "triple: %s" % list(triple)
    g.add(triple)

    # validate annotations (don't write garbage)
    #   maybe rdflib is doing this for us in g.parse & g.add?
    pass

    # write annotations file using storage service
    #   this should ask storage to up the repo version
    storage.put_file(identifier, "about.n3", g.serialize(format="n3"))

    # write annotation to central datastore
    #   push this off till future iteration
    __rdfstore_write(triple, ns_label, ns)
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
    try:
        store = rdflib.plugin.get('Sleepycat', rdflib.store.Store)('rdfstore')
        graph = rdflib.ConjunctiveGraph(store='Sleepycat',
                                        identifier=identifier)
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

