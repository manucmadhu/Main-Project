from django.db import models
class nuser:
    uuid=models.CharField(primary_key=True)
    name=models.CharField(max_length=100)
    user_id=models.CharField(unique=True,max_length=50)
    password=models.CharField(max_length=100)
    profile_pic = models.CharField(max_length = 500, blank=True)
    email = models.CharField(max_length = 100, blank=True)
    current_usage =models.IntegerField(blank=True)
    avg_usage=models.IntegerField(blank=True)
    bill_amount=models.IntegerField(default=0)
    pending=models.IntegerField(default=0)
    grid=models.CharField
    activity_status=models.BooleanField(default=True)
    
class appliance:
    uuid=models.CharField(primary_key=True)
    name=models.CharField(max_length=100)
    useruid=models.CharField(null=False)
    avg_consp=models.IntegerField
    
class generator:
    uuid=models.CharField(primary_key=True)
    fuel=models.CharField
    activity_status=models.BooleanField(default=True)
    curent_production=models.IntegerField
    peak_capcity=models.IntegerField
    grids=models.IntegerField
    #trying to link section from generators Note it

class section:
    uuid=models.CharField(primary_key=True)
    activity_status=models.BooleanField(default=True)
    grids=models.IntegerField
    users=models.IntegerField
    load=models.IntegerField
    gen=models.CharField(null=False,blank=False)


class grid:
    uuid=models.CharField(primary_key=True)
    activity_status=models.BooleanField(default=True)
    users=models.IntegerField
    load=models.IntegerField
    section=models.CharField

class bill:
    uuid=models.CharField(primary_key=True)
    useruid=models.CharField(null=False,blank=False)
    amount=models.IntegerField(blank=False,null=Flase)
    paid=models.BooleanField(default=False)