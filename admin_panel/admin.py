from django.contrib import admin
from users.models import User,appliance,generator,section,grid,bill,bear
# Register your models here.
admin.site.register(User)
admin.site.register(appliance)
admin.site.register(generator)
admin.site.register(section)
admin.site.register(grid)
admin.site.register(bill)
admin.site.register(bear)