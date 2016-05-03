# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-06 02:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rhea', '0008_auto_20160405_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirement',
            name='dependent',
            field=models.ForeignKey(help_text='\n\t        A pointer to a subject that requires the dependency - this stands for the forward side of\n\t        the relationship and allows for candidate estimation and progress tracking given a starting\n\t        set.\n\t    ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dependencies', to='rhea.Subject', verbose_name='dependent'),
        ),
        migrations.AlterField(
            model_name='student',
            name='subjects',
            field=models.ManyToManyField(help_text="\n            This is a list of pointers to subjects in the academic program's requirements tree,\n            or course plan. The list points to current subjects only - candidates are calculated\n            on demand by the schedule generator.\n        ", related_name='_student_subjects_+', to='rhea.Requirement', verbose_name='currently-coursing subjects'),
        ),
    ]
