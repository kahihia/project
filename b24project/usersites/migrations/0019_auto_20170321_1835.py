# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-21 18:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usersites', '0018_auto_20170321_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpage',
            name='src',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='landing', to='usersites.UserSite'),
        ),
    ]
