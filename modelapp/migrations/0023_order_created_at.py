# Generated by Django 5.0.6 on 2024-07-01 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0022_alter_transaction_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
