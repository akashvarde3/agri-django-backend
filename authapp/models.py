from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import json
class Farmer(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="farmer")
    agristack_id = models.CharField(max_length=100, blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.mobile})"
    
class Plot(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="plots")

    plot_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    user_provided_area = models.CharField(max_length=100, blank=True, null=True)
    calculated_area_sqm = models.FloatField()

    polygon_coordinates = models.JSONField()  # list of lat/lng pairs
    markers = models.JSONField()
    photo_geo = models.JSONField()           # lat/lng for photo
    photo_file = models.CharField(max_length=300, blank=True, null=True)

    status = models.JSONField(default=dict)  # can hold approval, flags, etc.

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plot_name} ({self.farmer.mobile})"


# Added CropCycle, HarvestEvent, ProductionHistory
class CropCycle(models.Model):
    plot=models.ForeignKey(Plot,on_delete=models.CASCADE,related_name="cycles")
    crop_name=models.CharField(max_length=100)
    area_acres=models.FloatField()
    sowing_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=50,default="Growing")
class HarvestEvent(models.Model):
    crop_cycle=models.ForeignKey(CropCycle,on_delete=models.CASCADE,related_name="harvests")
    harvested_on=models.DateField(auto_now_add=True)
    harvested_area_acres=models.FloatField(null=True,blank=True)
    harvested_qty=models.FloatField(null=True,blank=True)
    qr_url=models.CharField(max_length=255,null=True,blank=True)
    blockchain_tx=models.CharField(max_length=255,null=True,blank=True)
class ProductionHistory(models.Model):
    plot=models.ForeignKey(Plot,on_delete=models.CASCADE)
    crop_cycle=models.OneToOneField(CropCycle,on_delete=models.CASCADE)
    harvested_on=models.DateField()
    final_yield=models.FloatField(null=True,blank=True)
    qr_url=models.CharField(max_length=255)
    blockchain_tx=models.CharField(max_length=255)
