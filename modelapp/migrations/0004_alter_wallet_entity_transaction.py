# Generated by Django 5.0.6 on 2024-06-20 12:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0003_feedback_menu_qna_menuitem_order_ordereditem_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='entity',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], max_length=100)),
                ('payment_type', models.CharField(choices=[('CASH_ON_DELIVERY', 'Cash on Delivery'), ('STRIPE', 'Stripe')], max_length=100)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modelapp.order')),
            ],
            options={
                'indexes': [models.Index(fields=['order'], name='modelapp_tr_order_i_4d47bc_idx')],
            },
        ),
    ]
