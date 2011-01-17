from django.db import models

class Philes(models.Model):
    identifier = models.CharField(max_length=32)
    #check_sum  = models.CharField(max_length=32)
    #name = models.CharField(max_length=256)
    path = models.CharField(max_length=256)
    date_updated = models.DateTimeField()


    def id_exists(self, id):
        r = Philes.objects.filter(identifier=id)
        num = r.count()
        if (num == 0):
            return False 
        else:
            return True 

    def check_sum_exists(self, check_sum):
        r = Philes.objects.filter(check_sum=check_sum)
        if (r.count() == 0):
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
