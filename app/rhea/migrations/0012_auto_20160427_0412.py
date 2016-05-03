# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 04:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhea', '0011_auto_20160406_0234'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='last_confirmation',
            field=models.DateTimeField(default=None, editable=False, help_text="\n\t\t\tThe last date in which the instructor performed a status update. All active instructors\n\t\t\tare expected to do this. This date is not directly used other than by the token\n\t\t\tgenerator and exclusion strategies to determine who has performed the update and who\n\t\t\thasn't.\n\t\t", null=True, verbose_name='last update confirmation date'),
        ),
        migrations.AddField(
            model_name='student',
            name='last_confirmation',
            field=models.DateTimeField(default=None, editable=False, help_text="\n\t\t\tThe last date in which the student selected a course schedule. All active students\n\t\t\tare expected to do this. This date is not directly used other than by the token\n\t\t\tgenerator and exclusion strategies to determine who has performed the selection and\n\t\t\twho hasn't.\n\t\t", null=True, verbose_name='last update confirmation date'),
        ),
    ]
