# Generated by Django 5.0.6 on 2024-08-12 07:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0050_remove_message_modelapp_me_sender__69d65a_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reset_token', models.CharField(default='34fasdfq43asdtq43afsasrjytu', max_length=200)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['created_at', 'reset_token'], name='modelapp_pa_created_68cc8a_idx')],
            },
        ),
    ]
