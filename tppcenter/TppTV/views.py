from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from django.core.exceptions import ObjectDoesNotExist

from core.tasks import addTppAttrubute
from django.conf import settings

def get_news_list(request,page=1, id=None):
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
    current_section = "TPP-TV"

    if not id:
        newsPage = _newsContent(request, page)
    else:
        newsPage = _getdetailcontent(request, id)







    return render_to_response("TppTV/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'newsPage': newsPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _newsContent(request, page=1):
    news = TppTV.active.get_active().order_by('-pk')


    result = func.setPaginationForItemsWithValues(news, *('NAME', 'YOUTUBE_CODE', 'SLUG'), page_num=9, page=page)

    newsList = result[0]
    news_ids = [id for id in newsList.keys()]
    countries = Country.objects.filter(p2c__child__p2c__child__in=news_ids).values('p2c__child__p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, new in newsList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        new.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "tv:paginator"
    template = loader.get_template('TppTV/contentPage.html')
    context = RequestContext(request, {'newsList': newsList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator})
    return template.render(context)






def addNews(request):
    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')


    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
        user = request.user
        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('TppTV', values=values)
        form.clean()

        if form.is_valid():
            addTppAttrubute(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('tv:main'))





    return render_to_response('TppTV/addForm.html', {'form': form, 'categories': categories},
                              context_instance=RequestContext(request))



def updateNew(request, item_id):

    try:
        choosen_category = NewsCategories.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    categories = func.getItemsList('NewsCategories', 'NAME')
    if request.method != 'POST':



        form = ItemForm('TppTV', id=item_id)

    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)

        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('TppTV', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            addTppAttrubute(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('tv:main'))







    return render_to_response('TppTV/addForm.html', {'form': form, 'choosen_category': choosen_category,
                                                    'categories': categories},
                              context_instance=RequestContext(request))







def _getdetailcontent(request, id):
    new = get_object_or_404(TppTV, pk=id)
    newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE'))

    organizations = dict(Organization.objects.filter(p2c__child=new.pk).values('c2p__parent__country', 'pk'))
    try:
        newsCategory = NewsCategories.objects.get(p2c__child=id)
        category_value = newsCategory.getAttributeValues('NAME')
        newValues.update({'CATEGORY_NAME': category_value})
        similar_news = TppTV.objects.filter(c2p__parent__id=newsCategory.id).exclude(id=new.id)[:3]
        similar_news_ids = [sim_news.pk for sim_news in similar_news]
        similarValues = Item.getItemsAttributesValues(('NAME', 'DETAIL_TEXT', 'IMAGE', 'SLUG'), similar_news_ids)
    except ObjectDoesNotExist:
        similarValues = None
        pass


    if organizations.get('c2p__parent__country', False):
        countriesList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['c2p__parent__country'])
        toUpdate = {'COUNTRY_NAME': countriesList[organizations['c2p__parent__country']].get('NAME', [""]),
                    'COUNTRY_FLAG': countriesList[organizations['c2p__parent__country']].get('FLAG', [""]),
                    'COUNTRY_ID': organizations['c2p__parent__country']}
        newValues.update(toUpdate)


    if organizations.get('pk', False):
        organizationsList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['pk'])
        toUpdate = {'ORG_NAME': organizationsList[organizations['pk']].get('NAME', [""]),
                    'ORG_FLAG': organizationsList[organizations['pk']].get('FLAG', [""]),
                    'ORG_ID': organizations['pk']}
        newValues.update(toUpdate)



    template = loader.get_template('TppTV/detailContent.html')

    context = RequestContext(request, {'newValues': newValues, 'similarValues': similarValues})
    return template.render(context)
