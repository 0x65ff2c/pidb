# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-22 00:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tabby', '0006_remove_tuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.CharField(max_length=200),
        ),
    ]
