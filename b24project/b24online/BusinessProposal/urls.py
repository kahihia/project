from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.BusinessProposal.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', b24online.BusinessProposal.views.BusinessProposalList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', b24online.BusinessProposal.views.BusinessProposalList.as_view(), name="paginator"),
     url(r'^my/$', b24online.BusinessProposal.views.BusinessProposalList.as_view(my=True) , name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/', b24online.BusinessProposal.views.BusinessProposalList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', b24online.BusinessProposal.views.BusinessProposalCreate.as_view(), name="add"),
     url(r'^update/(?P<pk>[0-9]+)/$', b24online.BusinessProposal.views.BusinessProposalUpdate.as_view(), name="update"),
     url(r'^delete/(?P<pk>[0-9]+)/$', b24online.BusinessProposal.views.BusinessProposalDelete.as_view(), name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.BusinessProposal.views.BusinessProposalDetail.as_view(), name="detail"),
     url(r'^bp-category-list$', b24online.BusinessProposal.views.bp_categories_list,  name="BusinessProposalCategoryList"),

     url(r'^tabs/gallery/(?P<item>[0-9]+)/$', b24online.BusinessProposal.views.BPGalleryImageList.as_view(), name="tabs_gallery"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.BusinessProposal.views.BPGalleryImageList.as_view(), name="tabs_gallery_paged"),
     url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.BusinessProposal.views.BPGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$', b24online.BusinessProposal.views.DeleteBPGalleryImage.as_view(), name="gallery_remove_item"),

     url(r'^tabs/documents/(?P<item>[0-9]+)/$', b24online.BusinessProposal.views.BPDocumentList.as_view(), name="tabs_documents"),
     url(r'^tabs/documents/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.BusinessProposal.views.BPDocumentList.as_view(), name="tabs_documents_paged"),
     url(r'^tabs/documents_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.BusinessProposal.views.BPDocumentList.as_view(is_structure=True), name="documents_structure"),
     url(r'^tabs/documents/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$', b24online.BusinessProposal.views.DeleteBPDocument.as_view(), name="documents_remove_item"),
)
