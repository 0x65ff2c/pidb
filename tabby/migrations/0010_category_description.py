# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-27 04:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tabby', '0009_tuser_headimg'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
