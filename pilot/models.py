from __future__ import division
from django.db import models
from django.db.models import Sum
import datetime

class Philes(models.Model):
    identifier = models.CharField(max_length=32)
    num = models.IntegerField()
    sz = models.FloatField()
    obj_type = models.CharField(max_length=64)
    #check_sum  = models.CharField(max_length=32)
    #name = models.CharField(max_length=256)
    owner = models.CharField(max_length=32)
    path = models.CharField(max_length=256)
    date_updated = models.DateTimeField()


    def id_exists(self, id):
        r = Philes.objects.filter(identifier=id)
        num = r.count()
        if (num == 0):
            return False 
        else:
            return True 

    def get_phile(self, id):
        r = Philes.objects.get(identifier=id)
        return r

    def get_name(self, id):
        r = Philes.objects.get(identifier=id)
        if (r.count() > 0):
            return r.name
        else:
            return ""

    def get_path(self, id):
        r = Philes.objects.get(identifier=id)
        if (r.count() > 0):
            return r.path
        else:
            return "" 
    
    def get_stats(self, owner=None):
        o = 'dmc186'
        if owner:
            o = owner

        num_objects = len(Philes.objects.filter(owner=o)) 
        num_files = Philes.objects.filter(owner=o).aggregate(num=Sum('num'))
        ts = Philes.objects.filter(owner=o).aggregate(sz=Sum('sz'))
        # perhaps we should write a conversion function, but this'll work fer now
        if num_objects is 0:
            total_size = "0 MB"
        else:
            total_size = str(round(ts['sz'] / 1000000, 2)) + " MB"

        stats = { 'num_objects': num_objects, 'num_files': num_files['num'], 'total_size': total_size}
        return stats

class RDFMask(models.Model):
    phile = models.ForeignKey(Philes) 
    triple_predicate = models.CharField(max_length=256)
    triple_object = models.TextField()
    date_updated = models.DateTimeField(auto_now=True)


    """
    remove a metadata element
    """
    def remove_mask(self, id):
        r = RDFMask.objects.filter(pk=id)
        p = Philes.objects.filter(identifier=r[0].phile.identifier)
        r.delete()
        Log().logit(p[0], "MetadataDeleted")
        return


    """
    create an rdf triple in the database
    """
    def create_mask(self, sub, pred, obj):
        p = Philes.objects.get(identifier=sub)
        md = RDFMask(phile=p, triple_predicate=pred, triple_object=obj, date_updated=datetime.datetime.now() )
        md.save()
        action = "MetadataAdded"
        Log().logit(p, action)


    """
    update a triple in the database - for logging
    purposes, get the old/current meta key/value pair
    """
    def update_triple(self, pkey, pred, obj):
        mask = RDFMask.objects.get(pk=pkey)
        #action = "old metadata %s=>%s" % (mask.triple_predicate, mask.triple_object)
        #Log().logit(mask.phile, action)
        
        mask.triple_predicate = pred
        mask.triple_object = obj
        mask.date_updated = datetime.datetime.now()
        mask.save()

        #action = "new metadata %s=>%s" % (pred, obj)
        action = "MetadataEdited"
        Log().logit(mask.phile, action)
        return mask


    def get_md(self, p):
        md = RDFMask.objects.filter(phile=p).order_by('triple_predicate')
        return md

    """
    from a list of potential triple_object vals to represent
    an object title - query to get one to represent the object.
    if none exists - return the identifier
    """
    def get_title(self, p): 
        obj_title_predicates = ['title', 'subject']

        for pred in obj_title_predicates:
            result = RDFMask.objects.filter(phile__identifier=p.identifier).filter(triple_predicate=pred).order_by('id')
            if len(result):
                return result[0].triple_object

        return p.identifier

    """
    searches the table of meta data for searching
    """
    def search(self, keyword):
        matches = RDFMask.objects.filter(triple_object__contains=keyword).order_by('phile')
        return matches


    """
    get metadata values that start with the prefix value passed
    """
    def get_autocomplete(self, prefix):
        matches = RDFMask.objects.filter(triple_object__istartswith=prefix).values("triple_object").distinct()
        return matches


class Log(models.Model):
    phile = models.ForeignKey(Philes)
    action = models.CharField(max_length=256)
    user = models.CharField(max_length=32)
    date_updated = models.DateTimeField(auto_now=True)

    # two methods to log in terms of passed vals
    # pass either the ark or the phile

    # log action based on ark
    def logark(self, ark, act, u='dmc186'):
       p = Philes.objects.get(identifier=ark)
       self.logit(p, act, u)

    # log action based on phile
    def logit(self, p, act, u='dmc186'):
       l = Log(phile=p, action=act, user=u, date_updated=datetime.datetime.now() )
       l.save()

    # return all log events for an object/ark
    def get_log(self, ark):
        p = Philes.objects.get(identifier=ark)
        l = Log.objects.filter(phile=p)
        return l

class Audit(models.Model):
    phile = models.ForeignKey(Philes)
    result = models.TextField()
    valid = models.BooleanField()
    date_updated = models.DateTimeField(auto_now=True)

    def store_audit(self, ark, val, res=''):
        p = Philes.objects.get(identifier=ark)
        a = Audit(phile=p, valid=val, result=res)
        Log().logit(p, 'ObjectAudit')
        a.save()
        return a

    def get_last_audit(self, p):
        a = Audit.objects.filter(phile=p).order_by('-date_updated')
        if not a:
            return None
        else:
            return a[0]
