# Generated by Django 5.0.7 on 2024-07-17 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_payment_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
