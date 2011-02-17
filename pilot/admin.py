from pilot.models import Philes, RDFMask, AuditLog
from django.contrib import admin

class PhilesAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'num', 'sz', 'path', 'date_updated', 'owner')
    search_fields = ['identifier']

class RDFMaskAdmin(admin.ModelAdmin):
    list_display = ('phile','tuple_predicate', 'tuple_object')
    search_fields = ['tuple_predicate', 'tuple_object']

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('phile', 'action', 'user', 'date_updated')
    search_fields = ['phile', 'action', 'user']

admin.site.register(Philes, PhilesAdmin)
admin.site.register(RDFMask, RDFMaskAdmin)
admin.site.register(AuditLog, AuditLogAdmin)

