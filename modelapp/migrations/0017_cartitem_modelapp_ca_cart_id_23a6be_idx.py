# Generated by Django 5.0.6 on 2024-06-25 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0016_remove_cartitem_modelapp_ca_cart_id_23a6be_idx_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cartitem',
            index=models.Index(fields=['cart'], name='modelapp_ca_cart_id_23a6be_idx'),
        ),
    ]
