# Generated by Django 5.0.6 on 2024-06-27 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0021_alter_transaction_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
