from django.conf.urls import patterns, include, url
import appl.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'tpp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^news/$', appl.views.set_news_list),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/', appl.views.cabinet),
)
