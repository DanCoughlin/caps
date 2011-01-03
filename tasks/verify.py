import hashlib
from celery.decorators import task


@task
def generate(file_location, algorithm):
    h = hashlib.new(algorithm)
    h.update(open(file_location).read())
    return h.hexdigest() 
