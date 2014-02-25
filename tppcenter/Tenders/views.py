from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from core.tasks import addNewTender
from django.conf import settings

def get_tenders_list(request, page=1, item_id=None):
    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "Tenders"

    if item_id is None:
        tendersPage = _tendersContent(request, page)
    else:
        tendersPage = _tenderDetailContent(request, item_id)





    return render_to_response("Tenders/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'tendersPage': tendersPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _tendersContent(request, page=1):
    #TODO Jenya change to get_active_related()
    tenders = Tender.active.get_active().order_by('-pk')
    result = func.setPaginationForItemsWithValues(tenders, *('NAME', 'COST', 'CURRENCY', 'SLUG'), page_num=5, page=page)
    tendersList = result[0]
    tenders_ids = [id for id in tendersList.keys()]
    organizations = Organization.objects.filter(p2c__child__in=tenders_ids).values('c2p__parent__country', 'pk', 'p2c__child__tender')
    organization_dict = {}
    country_dict = {}
    for organization in organizations:
        organization_dict[organization['p2c__child__tender']] = organization['pk']
        country_dict[organization['p2c__child__tender']] = organization['c2p__parent__country']

    countriesList = Item.getItemsAttributesValues(('NAME', 'FLAG'), country_dict.values())
    organizationsList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organization_dict.values())


    for id, tender in tendersList.items():

        if organization_dict.get(id, False):
            orgToUpdate = {'ORG_NAME': organizationsList[organization_dict[id]].get('NAME', [""]),
                          'ORG_FLAG': organizationsList[organization_dict[id]].get('FLAG', [""]),
                          'ORG_ID': organization_dict[id]}
            tender.update(orgToUpdate)

        if country_dict.get(id, False):
            countryUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [""]),
                            'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [""]),
                            'COUNTRY_ID': country_dict[id]}
            tender.update(countryUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "tenders:paginator"
    template = loader.get_template('Tenders/contentPage.html')
    context = RequestContext(request, {'tendersList': tendersList, 'page': page,
                                       'paginator_range': paginator_range, 'url_paginator': url_paginator})
    return template.render(context)




def _tenderDetailContent(request, item_id):

     tender = get_object_or_404(Tender, pk=item_id)
     tenderValues = tender.getAttributeValues(*('NAME', 'COST', 'CURRENCY', 'START_EVENT_DATE', 'END_EVENT_DATE',
                                                 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3'))

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     country = Country.objects.get(p2c__child__p2c__child=item_id)




     company = Organization.objects.get(p2c__child=item_id)
     companyValues = company.getAttributeValues("NAME", 'FLAG', 'IMAGE')
     companyValues.update({'COMPANY_ID': company.id})


     countriesList = country.getAttributeValues("NAME", 'FLAG')
     toUpdate = {'COUNTRY_NAME': countriesList.get('NAME', 0),
                 'COUNTRY_FLAG': countriesList.get('FLAG', 0),
                 'COUNTRY_ID':  country.id}
     companyValues.update(toUpdate)

     template = loader.get_template('Tenders/detailContent.html')

     context = RequestContext(request, {'tenderValues': tenderValues, 'photos': photos,
                                        'additionalPages': additionalPages, 'companyValues': companyValues})
     return template.render(context)





def addTender(request):
    form = None
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()



    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tender', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            addNewTender(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('tenders:main'))

    return render_to_response('Tenders/addForm.html', {'form': form, 'currency_slots': currency_slots},
                              context_instance=RequestContext(request))



def updateTender(request, item_id):

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()


    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]




    form = ItemForm('Tender', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = _getValues(request)

        form = ItemForm('Tender', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            addNewTender(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('tenders:main'))







    return render_to_response('Tenders/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form,
                                                        'currency_slots': currency_slots, 'pages': pages},
                              context_instance=RequestContext(request))




def _getValues(request):

    values = {}
    values['NAME'] = request.POST.get('NAME', "")
    values['COST'] = request.POST.get('COST', "")
    values['CURRENCY'] = request.POST.get('CURRENCY', "")
    values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
    values['START_EVENT_DATE'] = request.POST.get('START_EVENT_DATE', "")
    values['END_EVENT_DATE'] = request.POST.get('END_EVENT_DATE', "")
    values['KEYWORD'] = request.POST.get('KEYWORD', "")
    values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
    values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
    values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")




    return values


