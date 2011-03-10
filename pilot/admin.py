from pilot.models import Philes, RDFMask, Log, Audit
from django.contrib import admin

class PhilesAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'obj_type', 'num', 'sz', 'path', 'date_updated', 'owner')
    search_fields = ['identifier']

class RDFMaskAdmin(admin.ModelAdmin):
    list_display = ('phile','triple_predicate', 'triple_object')
    search_fields = ['triple_predicate', 'triple_object']

class LogAdmin(admin.ModelAdmin):
    list_display = ('phile', 'action', 'user', 'date_updated')
    search_fields = ['phile', 'action', 'user']

class AuditAdmin(admin.ModelAdmin):
    list_display = ('phile', 'result', 'valid', 'date_updated')
    search_fields = ['phile', 'result', 'valid']

admin.site.register(Philes, PhilesAdmin)
admin.site.register(RDFMask, RDFMaskAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Audit, AuditAdmin)
