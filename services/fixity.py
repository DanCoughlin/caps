import hashlib
from pilot.models import Philes
#from tasks import verify


def generate(file_location, algorithm):
    h = hashlib.new(algorithm)
    h.update(open(file_location).read())
    return h.hexdigest() 
    #h = verify.generate.delay(file_location=file_location, algorithm=algorithm)
    #return h.get()
