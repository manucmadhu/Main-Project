# Generated by Django 5.1.4 on 2025-01-14 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_grid_sec1_grid_sec2_grid_sec3'),
    ]

    operations = [
        migrations.AddField(
            model_name='generator',
            name='grid1',
            field=models.CharField(default=0, max_length=50),
        ),
        migrations.AddField(
            model_name='generator',
            name='grid2',
            field=models.CharField(default=0, max_length=50),
        ),
    ]
