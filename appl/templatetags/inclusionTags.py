from django import template
from appl import func
from django.conf import settings
from appl.models import Cabinet, Organization, News, NewsCategories, UserSites, AdditionalPages, staticPages
from core.models import Item
from haystack.query import SearchQuerySet
from django.utils.translation import gettext as _
from django.db.models import Q
import os
from django.core.cache import cache

register = template.Library()

@register.inclusion_tag('AdvTop/tops.html', takes_context=True)
def getTopOnPage(context, item_id=None):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)


    cached = False
    cache_name = "adv_top_cache"

    #if filterAdv is None:
    #    cached = cache.get(cache_name)

    if not cached:
        tops = func.getTops(request, filterAdv)

        if filterAdv is None:
            cache.set(cache_name, tops, 60 * 60)
    else:
        tops = cache.get(cache_name)

    return {'MEDIA_URL': MEDIA_URL,  'modelTop': tops}

@register.inclusion_tag('AdvBanner/banners.html', takes_context=True)
def getBanners(context, item_id=None, *places):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    if item_id:
        filterAdv = func.getDeatailAdv(item_id)
    else:
        filterAdv = func.getListAdv(request)

    cached = False
    cache_name = "adv_banner_cache"

    #if filterAdv is None:
    #    cached = cache.get(cache_name)

    if not cached:
        banners = func.getBanners(places, settings.SITE_ID, filterAdv)

        if filterAdv is None:
            cache.set(cache_name, banners, 60 * 60)
    else:
        banners = cache.get(cache_name)


    return {'MEDIA_URL': MEDIA_URL, 'banners': banners}

@register.inclusion_tag('main/currentCompany.html', takes_context=True)
def getMyCompaniesList(context):

    request = context.get('request')


    if not request.user.first_name and not request.user.last_name:
        user_name = request.user.email
    else:
        user_name = request.user.first_name + ' ' + request.user.last_name

    current_company = request.session.get('current_company', False)

    cab = Cabinet.objects.get(user=request.user)
    #read all Organizations which hasn't foreign key from Department and current User is create user or worker

    companies = Organization.objects.filter(Q(create_user=request.user, department=None) |
                                                Q(p2c__child__p2c__child__p2c__child=cab.pk)).distinct()

    companies_ids = list(companies.values_list('pk', flat=True))


    if current_company is not False and current_company not in companies_ids:
        companies_ids.append(current_company)

    sqs = SearchQuerySet().filter(id__in=companies_ids).order_by('title')

    companies_ids = [company.id for company in sqs]

    if len(companies_ids) > 0:
        companies = Item.getItemsAttributesValues('NAME', companies_ids)
    else:
        companies = {}

    current = companies.get(current_company, False)

    if user_name == '':
        user_name = _('Profile')

    return {
        'companies': companies,
        'current': current,
        'currentId': current_company,
        'user': user_name,
        'current_path': request.get_full_path()
    }

@register.inclusion_tag('main/user_profile.html', takes_context=True)
def userProfile(context):

    request = context.get('request')
    cabinetValues = func.getB2BcabinetValues(request)
    MEDIA_URL = context.get('MEDIA_URL', '')

    return {
        'MEDIA_URL': MEDIA_URL,
        'cabinetValues': cabinetValues
    }

@register.inclusion_tag('News/last.html', takes_context=True)
def getLastNews(context):

    request = context.get('request')
    MEDIA_URL = context.get('MEDIA_URL', '')

    news = list(News.active.get_active().filter(c2p__parent__in=NewsCategories.objects.all()).order_by('-pk').values_list('pk', flat=True)[:3])
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news)



    return {'MEDIA_URL': MEDIA_URL,  'newsValues': newsValues }


@register.inclusion_tag('slider.html', takes_context=True)
def getUserSiteSlider(context):

    request = context.get('request')

    import glob


    user_site_slider = UserSites.objects.get(sites__id=settings.SITE_ID).getAttributeValues("TEMPLATE")
    file_count = 0
    if len(user_site_slider) > 0:


        user_site_slider = user_site_slider[0]

        slider_dir = 'tppcenter/img/templates/' + user_site_slider

        dir = os.path.join(settings.MEDIA_ROOT, slider_dir).replace('\\', '/')

        file_count = len(glob.glob(dir+"/*.jpg"))




    return {'file_count':file_count ,  'user_site_slider': user_site_slider}


@register.inclusion_tag('site_sidebar.html', takes_context=True)
def getUserSiteMenu(context):

    midea_url = settings.MEDIA_URL

    user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
    organization = user_site.organization.pk

    additionalPages = AdditionalPages.objects.filter(c2p__parent=organization).values_list('pk', flat=True)
    addPagesValues = Item.getItemsAttributesValues(('NAME',), additionalPages)

    return {'addPagesValues': addPagesValues, 'midea_url': midea_url }

@register.inclusion_tag('main/staticPages.html')
def showStaticPages():

    pages = [page.pk for page in staticPages.objects.all()]

    pageWithAttr = Item.getItemsAttributesValues(('SLUG', 'NAME'), pages)

    pages = {}

    for page in staticPages.objects.all():

        name = pageWithAttr[page.pk].get('NAME', [""])[0]
        slug = pageWithAttr[page.pk].get('SLUG', [""])[0]

        if page.pageType not in pages:
            pages[page.pageType] = []

        pages[page.pageType].append((slug, name))


    return {'pagesDict': pages}


@register.inclusion_tag('main/topStaticPages.html')
def showTopStaticPages():

    pages = [page.pk for page in staticPages.objects.filter(onTop=True)]

    pageWithAttr = Item.getItemsAttributesValues(('SLUG', 'NAME'), pages)

    return {'pagesDict': pageWithAttr}

