from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('user', 'User')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='user')
    uuid=models.CharField(max_length=50,primary_key=True)
    name=models.CharField(max_length=100,default=None,null=True)
    username=models.CharField(unique=True,max_length=50)
    password=models.CharField(max_length=100)
    profile_pic = models.CharField(max_length = 500,null=True)
    email = models.EmailField(max_length=255,null=True)
    current_usage =models.IntegerField(blank=True,default=0,null=True)
    avg_usage=models.IntegerField(blank=True,default=0,null=True)
    bill_amount=models.IntegerField(default=0,null=True)
    pending=models.IntegerField(default=0,null=True)
    grid=models.CharField(max_length=50,default='-1',null=True,)
    activity_status=models.BooleanField(default=True,null=True)
    
class appliance(models.Model):
    uuid=models.CharField(primary_key=True,max_length=50)
    name=models.CharField(max_length=100)
    useruid=models.CharField(null=False,max_length=100)
    avg_consp=models.IntegerField(default=0)
    
class generator(models.Model):
    uuid=models.CharField(primary_key=True,max_length=50)
    fuel=models.CharField(max_length=3)
    activity_status=models.BooleanField(default=True)
    curent_production=models.IntegerField(default=0)
    peak_capcity=models.IntegerField(default=0)
    grids=models.IntegerField(default=0)
    #trying to link section from generators Note it

class section(models.Model):
    uuid=models.CharField(primary_key=True,max_length=50)
    activity_status=models.BooleanField(default=True)
    grids=models.IntegerField(default=0)
    users=models.IntegerField(default=0)
    load=models.IntegerField(default=0)
    gen=models.CharField(null=False,blank=False,max_length=50)


class grid(models.Model):
    uuid=models.CharField(primary_key=True,max_length=50)
    activity_status=models.BooleanField(default=True)
    users=models.IntegerField(default=0)
    load=models.IntegerField(default=0)
    section=models.CharField(max_length=50)

class bill(models.Model):
    uuid=models.CharField(primary_key=True,max_length=50)
    useruid=models.CharField(null=False,blank=False,max_length=100)
    amount=models.IntegerField(blank=False,null=False)
    paid=models.BooleanField(default=False)

