import rdflib
import StringIO
from datetime import datetime
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
    #   * subject is ark://42409/foobarid
    #   * property is http://purl.org/dc/terms/title
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

    # instantiate a graph
    g = rdflib.ConjunctiveGraph()

    if annotations:
        # pull existing annotations into in-memory rdf graph
        g.parse(StringIO(annotations), format="n3")

    # attach annotation to annotations file
    g.add(rdflib.URIRef(annotation[0]),
          rdflib.Namespace(annotation[1]),
          rdflib.Literal(annotation[2]))

    # validate annotations (don't write garbage)
    #   maybe rdflib is doing this for us in g.parse & g.add?
    pass

    # write annotations file using storage service
    #   this should ask storage to up the repo version
    storage.put_file(identifier, "about.n3", g.serialize(format="n3"))

    # write annotation to central datastore
    #   push this off till future iteration
    pass

    return True
