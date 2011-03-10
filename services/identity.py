import os
import re
import datetime
import arkpy
from pilot.models import Philes, Log
#from tasks import identify as identify_task

def mint():
    ark = arkpy.mint(authority='42409', template='eeddeeddk', bare=False)
    return ark
    #ark = identify_task.mint.delay(authority='42409', template='eeddeeddk')
    #return ark.get()

def validate(ark):
    is_valid = arkpy.validate(ark)
    return is_valid
    #is_valid = identify_task.validate.delay(ark)
    #return is_valid.get()

def mint_new():
    id = mint()
    # while the id exists get me a new one
    while exists(id):
        id = mint()
    return id

def exists(id):
    return Philes().id_exists(id)        

def lookup(id):
    return Philes().get_phile(id) 
       
def bind(id, full_path, uid, o_sz, o_num=1, o_type='compound' ):
    p = Philes(identifier=id, path=full_path, owner=uid, date_updated=datetime.datetime.now(), sz=o_sz, num=o_num, obj_type=o_type ) 

    p.save()
    Log().logit(p, "ObjectIdAssigned")

def remove_scheme(id):
    try:
        return re.compile("\w+:/+(.+)").search(id).groups()[0]
    except:
        return id
