from django.db import models
from datetime import datetime,timedelta,timezone
# Create your models here.
class ConfigurationValue(models.Model):
    configurationValueId = models.AutoField(primary_key=True)
    configurationId = models.IntegerField(null=False,default=0)
    plant = models.CharField(max_length=4,null=True,blank=True)
    workCenter= models.CharField(max_length=10,null=True,blank=True)
    confgObject = models.CharField(max_length=50,null=True,blank=True)
    confgKey = models.CharField(max_length=50, null=False)
    keyValue = models.CharField(max_length=100, null=False)
    comments = models.CharField(max_length=250,null=True,blank=True)

class MaterialPullLog(models.Model):
    autoId = models.AutoField(primary_key=True)
    plant = models.CharField(max_length=4, null=False)
    materialNumber = models.CharField(max_length=18, null=False)
    requestZoneId = models.CharField(max_length=100, null=False)
    requestTimeStamp = models.DateTimeField(auto_now=True,blank=True)
    acknowledgeTimeStamp = models.DateTimeField(null=True,blank=True)
    enrouteTimeStamp= models.DateTimeField(null=True,blank=True)
    deliveredTimeStamp = models.DateTimeField(null=True,blank=True)
    processed = models.CharField(max_length=1)
    transferOrderNumber = models.CharField(max_length=20, editable=False)
    tagId = models.CharField(max_length=10,null=False,default=None)

    def save(self, *args, **kwargs):
        if not self.transferOrderNumber:
        # Generate the transfer order number based on your requirements
        # For example, you can combine a prefix with a timestamp
            prefix = "TO-"
            timestamp = datetime.now().strftime("%m%d%Y%H%M%S")
            self.transferOrderNumber = f"{prefix}{timestamp}"
            self.acknowledgeTimeStamp= datetime.now(timezone.utc) + timedelta(0,5)
            super().save(*args, **kwargs)
        elif self.transferOrderNumber:
            super().save(*args, **kwargs)

class TagLog(models.Model):
    tagId = models.CharField(max_length=10)
    zoneId = models.CharField(max_length=10)
    zoneEnteredTimeStamp = models.DateTimeField(null=True,blank=True)
    zoneExitTimeStamp = models.DateTimeField(null=True,blank=True)
    batteryPercentage = models.CharField(max_length=5)
    transferOrderNumber = models.CharField(max_length=20)
    materialNumber = models.CharField(max_length=18,null=False)
    zoneName =  models.CharField(max_length=10)








