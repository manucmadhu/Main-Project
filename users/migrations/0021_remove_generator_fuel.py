# Generated by Django 5.1.4 on 2025-02-17 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_alter_generator_fuel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generator',
            name='fuel',
        ),
    ]
