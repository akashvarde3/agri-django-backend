from django.db import models
from django.contrib.auth.hashers import make_password, check_password

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
