# Generated by Django 5.1.3 on 2025-01-01 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_alter_category_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='slug',
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
