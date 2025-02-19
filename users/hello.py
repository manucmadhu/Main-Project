from users.models import bear
for b in bear.objects.all():
    print(b.name)