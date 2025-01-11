from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('user', 'User')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    groups = models.ManyToManyField(Group, related_name="user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_permissions_user", blank=True)

class bear(models.Model):
    admin=models.IntegerField(default=0)
    uuid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, default=None, blank=True, null=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True,unique=True)
    current_usage = models.IntegerField(default=0, blank=True, null=True)
    avg_usage = models.IntegerField(default=0, blank=True, null=True)
    bill_amount = models.IntegerField(default=0, blank=True, null=True)
    pending = models.IntegerField(default=0, blank=True, null=True)
    grid = models.ForeignKey('Grid', on_delete=models.SET_NULL, null=True, blank=True)
    activity_status = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='bear_users', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='bear_user_permissions', blank=True)
    # REQUIRED_FIELDS = ['uuid']
    # USERNAME_FIELD = 'email'
    # is_anonymous = False
    # is_authenticated=False
    
class appliance(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(bear, on_delete=models.CASCADE, related_name='appliances')
    avg_consp = models.IntegerField(default=0)

class generator(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    fuel = models.CharField(max_length=3)
    activity_status = models.BooleanField(default=True)
    current_production = models.IntegerField(default=0)
    peak_capacity = models.IntegerField(default=0)
    sections = models.ManyToManyField('Section', related_name='generators')

class section(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    activity_status = models.BooleanField(default=True)
    grids = models.ManyToManyField('Grid', related_name='sections')
    users = models.IntegerField(default=0)
    load = models.IntegerField(default=0)

class grid(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    activity_status = models.BooleanField(default=True)
    users = models.IntegerField(default=0)
    load = models.IntegerField(default=0)

class bill(models.Model):
    uuid = models.CharField(primary_key=True, max_length=50)
    user = models.ForeignKey(bear, on_delete=models.CASCADE, related_name='bills')
    amount = models.IntegerField()
    paid = models.BooleanField(default=False)

# user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Assuming '1' is a valid default User
