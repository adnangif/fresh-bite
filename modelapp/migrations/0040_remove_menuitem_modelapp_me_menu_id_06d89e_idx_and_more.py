# Generated by Django 5.0.6 on 2024-07-28 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0039_rename_restaurantlocation_deliveryzone_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='menuitem',
            name='modelapp_me_menu_id_06d89e_idx',
        ),
        migrations.AddIndex(
            model_name='menuitem',
            index=models.Index(fields=['menu', 'name'], name='modelapp_me_menu_id_4960b9_idx'),
        ),
    ]
