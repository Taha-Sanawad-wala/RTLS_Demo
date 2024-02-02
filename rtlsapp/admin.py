from django.contrib import admin
from rtlsapp.models import ConfigurationValue, MaterialPullLog,TagLog 
# Register your models here.
class ConfigurationValueAdmin(admin.ModelAdmin):
    list_display = ['configurationValueId','plant','workCenter','confgObject','confgKey','keyValue','comments']

class MaterialPullLogAdmin(admin.ModelAdmin):
    list_display = ['autoId','plant','materialNumber','requestZoneId','requestTimeStamp','acknowledgeTimeStamp', 'enrouteTimeStamp','deliveredTimeStamp','processed','transferOrderNumber','tagId' ]

class TagLogAdmin(admin.ModelAdmin):
    list_display = ["tagId","zoneId","zoneEnteredTimeStamp","zoneExitTimeStamp","transferOrderNumber","materialNumber","zoneName"]
admin.site.register(ConfigurationValue,ConfigurationValueAdmin)
admin.site.register(MaterialPullLog,MaterialPullLogAdmin)
admin.site.register(TagLog,TagLogAdmin)