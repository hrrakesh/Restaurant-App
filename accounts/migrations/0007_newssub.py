# Generated by Django 5.1.3 on 2024-12-29 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_userprofile_city_alter_userprofile_country_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsSub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=25, unique=True)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
