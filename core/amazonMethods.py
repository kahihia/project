from __future__ import absolute_import
from core.models import Item

from appl import func
from PIL import Image
from django.conf import settings
from django.utils.timezone import now
import tinys3
import uuid
import time
import os
from celery import shared_task






def add(imageFile=None, toDelete=None):

    sizes = {
        'big': {'box': (500, 500), 'fit': False},
        'small': {'box': (200, 200), 'fit': False},
        'th': {'box':(80, 80), 'fit': True}
    }

    name = str(uuid.uuid4())
    i = now()
    folder = "%s/%s/%s" % (i.day, i.month, i.year)



    #time.sleep(60)

    if imageFile:
        try:


            im = Image.open(imageFile)
            requests = []

            # Creating a pool connection
            pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                         endpoint='s3.amazonaws.com')

            for type, size in sizes.items():
                path = '/' + type + '/'+ folder + '/' + name + '.jpg'
                out = settings.MEDIA_ROOT + '/' + type + '-' + name + '.jpg'
                func.resize(im, out=out, **size)

                f = open(out, 'rb')

                # Uploading a single file
                #f = open('some_file.zip','rb')
                requests.append(pool.upload(path, f, close=True))
                if isinstance(toDelete, list):
                    for delete in toDelete:
                        filename = type + '/' + delete
                        requests.append(pool.delete(filename)) if toDelete else ''


            f = open(imageFile, 'rb')
            if isinstance(toDelete, list):
                    for delete in toDelete:
                        filename = delete
                        requests.append(pool.delete(filename)) if toDelete else ''

            requests.append(pool.upload(folder + '/' + name + '.jpg', f, close=True))
            pool.all_completed(requests)



            filename = imageFile
            if os.path.isfile(filename):
                    os.remove(filename)
            for key in sizes.keys():
                filename = '%s-%s' % (key, name + '.jpg')
                filename = '%s/%s' % (settings.MEDIA_ROOT, filename)
                if os.path.isfile(filename):
                     os.remove(filename)




        except Exception as e:
            raise e


    return folder + '/' + name + '.jpg'


def delete(toDelete=None):
     sizes = ['big', 'small', 'th']

     pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                                                endpoint='s3.amazonaws.com')
     requests = []
     if not toDelete:
         return False
     try:
         for delete in toDelete:
            filename = delete
            requests.append(pool.delete(filename))
         for size in sizes:
            for delete in toDelete:
                filename = size + '/' + delete
                requests.append(pool.delete(filename))

         pool.all_completed(requests)
     except Exception:
         return False

     return True


