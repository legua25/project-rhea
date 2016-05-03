# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 03:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhea', '0003_auto_20160324_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='title',
            field=models.CharField(default='', help_text="\n\t\t\tBecause instructors have spent lots of time to earn that nice title of theirs,\n\t\t\tshouldn't we just provide them a way to showcase it?\n\t\t", max_length=16, verbose_name='title'),
            preserve_default=False,
        ),
    ]
