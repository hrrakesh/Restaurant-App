# Generated by Django 5.1.3 on 2025-01-20 16:21

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_remove_userprofile_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
