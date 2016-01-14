from django.conf.urls import url
from django.views.generic import TemplateView

from usersites.OrganizationPages.views import Contacts, PageDetail, Structure

urlpatterns = [
    url(r'^about$', TemplateView.as_view(template_name='usersites/OrganizationPages/about.html'), name='about'),
    url(r'^structure$', Structure.as_view(), name='structure'),
    url(r'^contacts/$', Contacts.as_view(), name='contacts'),
    url(r'^gallery/$', TemplateView.as_view(template_name='usersites/OrganizationPages/gallery.html'), name='gallery'),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', PageDetail.as_view(), name='detail'),
]
