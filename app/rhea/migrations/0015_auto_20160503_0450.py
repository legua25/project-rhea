# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 04:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rhea', '0014_auto_20160503_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseschedule',
            name='entries',
            field=models.ManyToManyField(help_text='\n\t\t\tThis indicates a course is to be taken by a student or instructed by an instructor. Since\n\t\t\tthis data is collected into the individual course object, we can relax the relationship and\n\t\t\tuse courses as the middle-man between students, instructors, subjects, and time slots.\n\t\t\tProgramming time is just so much fun!\n\t\t', related_name='schedule', related_query_name='schedule', to='rhea.Course', verbose_name='schedule entries'),
        ),
    ]
