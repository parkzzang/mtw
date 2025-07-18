# Generated by Django 5.2 on 2025-04-14 16:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_licenseverification_reviewed_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='profile_photos/')),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
                ('bio', models.TextField(blank=True)),
                ('height', models.PositiveIntegerField(blank=True, help_text='cm', null=True)),
                ('weight', models.PositiveIntegerField(blank=True, help_text='kg', null=True)),
                ('is_smoker', models.BooleanField(blank=True, null=True)),
                ('religion', models.CharField(blank=True, max_length=20)),
                ('interests', models.CharField(blank=True, max_length=100)),
                ('mbti', models.CharField(blank=True, max_length=4)),
                ('ideal_type', models.TextField(blank=True, verbose_name='원하는 매칭 조건')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
