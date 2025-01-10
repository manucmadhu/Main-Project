from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid
class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('user', 'User')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='user')
#     uuid=models.CharField(max_length=50,primary_key=True,unique=True,default=0)
#     name=models.CharField(max_length=100,default=None)
#     username=models.CharField(unique=True,max_length=50)
#     password=models.CharField(max_length=100)
#     profile_pic = models.CharField(max_length = 500, blank=True)
#     email = models.CharField(max_length = 100, blank=True)
#     current_usage =models.IntegerField(blank=True,default=0)
#     avg_usage=models.IntegerField(blank=True,default=0)
#     bill_amount=models.IntegerField(default=0)
#     pending=models.IntegerField(default=0)
#     grid=models.CharField(max_length=50,default='0')
#     activity_status=models.BooleanField(default=True)

class appliance:
    uuid=models.CharField(primary_key=True)
    name=models.CharField(max_length=100)
    useruid=models.CharField(null=False)
    avg_consp=models.IntegerField(default=0)
    
class generator:
    uuid=models.CharField(primary_key=True)
    fuel=models.CharField(max_length=3)
    activity_status=models.BooleanField(default=True)
    curent_production=models.IntegerField(default=0)
    peak_capcity=models.IntegerField(default=0)
    grids=models.IntegerField(default=0)
    #trying to link section from generators Note it

class section:
    uuid=models.CharField(primary_key=True)
    activity_status=models.BooleanField(default=True)
    grids=models.IntegerField(default=0)
    users=models.IntegerField(default=0)
    load=models.IntegerField(default=0)
    gen=models.CharField(null=False,blank=False)


class grid:
    uuid=models.CharField(primary_key=True)
    activity_status=models.BooleanField(default=True)
    users=models.IntegerField(default=0)
    load=models.IntegerField(default=0)
    section=models.CharField(max_length=50)

class bill:
    uuid=models.CharField(primary_key=True)
    useruid=models.CharField(null=False,blank=False)
    amount=models.IntegerField(blank=False,null=False)
    paid=models.BooleanField(default=False)