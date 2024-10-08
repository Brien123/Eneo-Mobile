# Generated by Django 5.0.7 on 2024-08-23 06:14

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.TextField(max_length=2000)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to=settings.AUTH_USER_MODEL)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='users.messages')),
            ],
        ),
    ]
