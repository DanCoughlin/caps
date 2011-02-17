from django.db import models
import datetime

class Philes(models.Model):
    identifier = models.CharField(max_length=32)
    num = models.IntegerField()
    sz = models.FloatField()
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

class RDFMask(models.Model):
    phile = models.ForeignKey(Philes) 
    tuple_predicate = models.CharField(max_length=256)
    tuple_object = models.TextField()
    date_updated = models.DateTimeField()

    def create_mask(self, sub, pred, obj):
        p = Philes.objects.get(identifier=sub)
        md = RDFMask(phile=p, tuple_predicate=pred, tuple_object=obj, date_updated=datetime.datetime.now() )
        md.save()
        action = "adding metadata %s=>%s" % (pred, obj)
        AuditLog().logit(p, action)

    def get_md(self, p):
        md = RDFMask.objects.filter(phile=p)
        return md

class AuditLog(models.Model):
    phile = models.ForeignKey(Philes)
    action = models.CharField(max_length=256)
    user = models.CharField(max_length=32)
    date_updated = models.DateTimeField()

    # two methods to log in terms of passed vals
    # pass either the ark or the phile

    # log action based on ark
    def logark(self, ark, act, u='dmc186'):
       p = Philes.objects.get(identifier=ark)
       self.logit(p, act, u)

    # log action based on phile
    def logit(self, p, act, u='dmc186'):
       al = AuditLog(phile=p, action=act, user=u, date_updated=datetime.datetime.now() )
       al.save()
