# Generated by Django 5.1.3 on 2025-01-20 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_userprofile_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='location',
        ),
    ]
