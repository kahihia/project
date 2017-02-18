# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-22 19:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0016_auto_20160607_0902'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalpage',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='additionalpage',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='additionalpage',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='b2bproduct',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='b2bproduct',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='b2bproduct',
            name='name_es',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='b2bproduct',
            name='short_description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='b2bproduct',
            name='slug_es',
            field=models.SlugField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='b2bproductcategory',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='b2bproductcategory',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='banner',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bannerblock',
            name='description_es',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='bannerblock',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='branch',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='branch',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='businessproposal',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='businessproposal',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='businessproposal',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='businessproposal',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='businessproposalcategory',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='businessproposalcategory',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='address_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='director_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='short_description_es',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chamber',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='address_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='director_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='short_description_es',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='description_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='city_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='route_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='gallery',
            name='title_es',
            field=models.CharField(max_length=266, null=True),
        ),
        migrations.AddField(
            model_name='greeting',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='greeting',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='greeting',
            name='organization_name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='greeting',
            name='position_name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='greeting',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='business_plan_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='name_es',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='product_name_es',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='innovationproject',
            name='slug_es',
            field=models.SlugField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='short_description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='newscategory',
            name='name_es',
            field=models.CharField(db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='newscategory',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='producer',
            name='name_es',
            field=models.CharField(max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='producer',
            name='short_description_es',
            field=models.TextField(blank=True, null=True, verbose_name='Short description'),
        ),
        migrations.AddField(
            model_name='producer',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='first_name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_name_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='middle_name_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='profession_es',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='description_es',
            field=models.TextField(blank=True, null=True, verbose_name='Descripion'),
        ),
        migrations.AddField(
            model_name='question',
            name='question_text_es',
            field=models.TextField(null=True, verbose_name='Question text'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='description_es',
            field=models.TextField(blank=True, null=True, verbose_name='Descripion'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='name_es',
            field=models.CharField(max_length=255, null=True, verbose_name='Questionnaire title'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='short_description_es',
            field=models.TextField(blank=True, null=True, verbose_name='Short description'),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='description_es',
            field=models.TextField(blank=True, null=True, verbose_name='Descripion'),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tender',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='tender',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='tender',
            name='slug_es',
            field=models.SlugField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='tender',
            name='title_es',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='name_es',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='content_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='keywords_es',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='short_description_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='slug_es',
            field=models.SlugField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='title_es',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
