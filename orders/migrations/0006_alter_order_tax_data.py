# Generated by Django 5.1.3 on 2025-01-20 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_total_data_order_vendors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tax_data',
            field=models.JSONField(blank=True, help_text="Data Format: {'tax_type':{'tax_percentage': 'tax_amount'}}", null=True),
        ),
    ]
