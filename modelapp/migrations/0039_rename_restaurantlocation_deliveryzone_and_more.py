# Generated by Django 5.0.6 on 2024-07-27 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0038_location_location_in_string_restaurantlocation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RestaurantLocation',
            new_name='DeliveryZone',
        ),
        migrations.RenameIndex(
            model_name='deliveryzone',
            new_name='modelapp_de_restaur_856502_idx',
            old_name='modelapp_re_restaur_41082a_idx',
        ),
    ]
