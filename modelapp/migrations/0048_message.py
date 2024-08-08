# Generated by Django 5.0.6 on 2024-08-08 06:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelapp', '0047_person_ride_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('message_sent_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='modelapp.order')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['sender'], name='modelapp_me_sender__69d65a_idx'), models.Index(fields=['receiver'], name='modelapp_me_receive_ee3dea_idx'), models.Index(fields=['message_sent_at'], name='modelapp_me_message_3eab41_idx')],
            },
        ),
    ]
