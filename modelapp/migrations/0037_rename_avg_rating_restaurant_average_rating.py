# Generated by Django 5.0.6 on 2024-07-23 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0036_rename_rating_restaurant_avg_rating_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='restaurant',
            old_name='avg_rating',
            new_name='average_rating',
        ),
    ]
