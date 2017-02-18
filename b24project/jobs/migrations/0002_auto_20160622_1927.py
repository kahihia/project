# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-22 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='city_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='requirements_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='terms_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='additional_information_es',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='additional_skill_es',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='additional_study_es',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='address_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='company_exp_1_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='company_exp_2_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='company_exp_3_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='computer_skill_es',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='faculty_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='institution_es',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='language_skill_es',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='nationality_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='position_exp_1_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='position_exp_2_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='position_exp_3_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='profession_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
