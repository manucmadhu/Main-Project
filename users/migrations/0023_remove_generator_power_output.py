# Generated by Django 5.1.4 on 2025-02-19 04:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_alter_generator_generator_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generator',
            name='power_output',
        ),
    ]
