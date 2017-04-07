# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-21 13:26
from __future__ import unicode_literals

import b24online.custom
import b24online.utils
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usersites', '0016_landingpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpage',
            name='image',
            field=b24online.custom.CustomImageField(blank=True, max_length=255, null=True, storage=b24online.custom.S3ImageStorage(), upload_to=b24online.utils.generate_upload_path),
        ),
    ]