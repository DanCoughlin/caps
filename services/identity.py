import os
import re
import datetime
import arkpy
from pilot.models import Philes, AuditLog
#from tasks import identify as identify_task

def mint():
    ark = arkpy.mint(authority='42409', template='eeddeeddk')
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
       
def bind(id, full_path, uid, obj_sz, obj_num=1 ):
    p = Philes(identifier=id, path=full_path, owner=uid, date_updated=datetime.datetime.now(), sz=obj_sz, num=obj_num ) 

    p.save()
    AuditLog().logit(p, "binding ark and object")

def remove_scheme(id):
    try:
        return re.compile("\w+:/+(.+)").search(id).groups()[0]
    except:
        return id
