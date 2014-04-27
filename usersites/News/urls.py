from django.conf.urls import patterns, url, include
from django.contrib import admin

import usersites.News.views
import usersites.views
import tppcenter.urls


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.News.views.get_news_list, name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', usersites.News.views.get_news_list, name="paginator"),
     url(r'^(?P<slug>[0-9a-zA-z-]+-(?P<item_id>[0-9]+))\.html$', usersites.News.views.get_news_list, name='detail'),

)