# Generated by Django 5.0.6 on 2024-06-21 10:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0008_alter_restaurant_closes_at_alter_restaurant_opens_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modelapp.restaurant'),
        ),
    ]
