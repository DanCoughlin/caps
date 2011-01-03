import datetime
import os
import arkpy
from pilot.models import Philes
#from tasks import identify as identify_task

def mint():
    ark = arkpy.mint(authority='42409', template='eeddeeddk')
    return ark
    #ark = identify_task.mint.delay(authority='42409', template='eeddeeddk')
    #return ark.get()

def validate(ark=''):
    is_valid = arkpy.validate(ark)
    return is_valid
    #is_valid = identify_task.validate.delay(ark)
    #return is_valid.get()

def exists(id):
    return Philes().id_exists(id)        

def lookup(id):
    return Philes().get_phile(id) 
       
def bind(id, full_path, check_sum=''):
    base = os.path.basename(full_path)
    folder = os.path.dirname(full_path)
    p = Philes(identifier=id, name=base, path=folder, check_sum=check_sum, date_updated=datetime.datetime.now() ) 
    p.save()

