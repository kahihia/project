from django.conf.urls import patterns, include, url

import centerpokupok.Company.views

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', centerpokupok.Company.views.storeMain, name="main"),
     url(r'^category(?P<category>[0-9]+)/$', centerpokupok.Company.views.storeMain, name="category"),
     url(r'^products/$', centerpokupok.Company.views.companyProductList.as_view(), name="products"),
     url(r'^products/page(?P<page>[0-9]+)/$', centerpokupok.Company.views.companyProductList.as_view(), name="products_paged"),
     url(r'^products/category(?P<category>[0-9]+)/$', centerpokupok.Company.views.companyProductList.as_view(), name="products_category"),
     url(r'^products/category(?P<category>[0-9]+)/page(?P<page>[0-9]+)/$',
         centerpokupok.Company.views.companyProductList.as_view(), name="products_category_paged"),
     url(r'^coupons/$', centerpokupok.Company.views.companyCoupontList.as_view(), name="coupons"),
     url(r'^coupons/page(?P<page>[0-9]+)/$', centerpokupok.Company.views.companyCoupontList.as_view(), name="coupons_paged"),
     url(r'^coupons/category(?P<category>[0-9]+)/$', centerpokupok.Company.views.companyCoupontList.as_view(), name="coupons_category"),
     url(r'^coupons/category(?P<category>[0-9]+)/page(?P<page>[0-9]+)/$',
         centerpokupok.Company.views.companyCoupontList.as_view(), name="coupons_category_paged"),
     url(r'^about/$', centerpokupok.Company.views.about, name="about"),
     url(r'^contact/$', centerpokupok.Company.views.contact, name="contact"),
)