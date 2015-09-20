from copy import copy
import hashlib
from urllib.parse import urlparse
import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import QueryDict
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.timezone import make_aware, is_naive, get_current_timezone, now
from django.db.models import F, Q
from django.core.paginator import Paginator
from PIL import Image
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from haystack.query import SearchQuerySet, SQ
import lxml
from lxml.html.clean import clean_html

from appl.models import Category, Tpp, Cabinet, SystemMessages
from b24online.models import Chamber, InnovationProject, News, Company, BusinessProposal, Exhibition, Country, Branch, \
    Organization, Notification, B2BProduct, Banner, B2BProductCategory, BusinessProposalCategory
from b24online.search_indexes import CountryIndex, ChamberIndex, BranchIndex, B2bProductCategoryIndex, \
    BusinessProposalCategoryIndex, SearchEngine
from core.models import Item
from jobs.models import Requirement
from tpp.SiteUrlMiddleWare import get_request


def get_paginator_range(page):
    '''
    Method that get page object and return paginatorRange ,
    help to  display properly pagination
    Example
    result = func.getItemsListWithPagination("News", "NAME", "Active_From", "DETAIL_TEXT", "IMAGE", page=4)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page) Pass this object to template

    '''
    if page.number - 2 > 0:
        start = page.number - 2
    else:
        start = 1
    if start + 5 <= page.paginator.num_pages:
        end = start + 5
    else:
        end = page.paginator.num_pages + 1

    paginator_range = range(start, end)
    return paginator_range


def setPaginationForSearchWithValues(items, *attr, page_num=10, page=1, fullAttrVal=False):
    '''
    Method  return List of Values of items and  Pagination
    items = QuerySet of items
    attr = (list of item's attributes)
    page = number of current page
    page_num = num element per page
    '''
    paginator = Paginator(items, page_num)
    try:
        page = items = paginator.page(page)
    except Exception:
        page = items = paginator.page(1)
    if not isinstance(items, list):
        items = tuple([item.pk for item in page.object_list])
    attributeValues = Item.getItemsAttributesValues(attr, items, fullAttrVal)

    return attributeValues, page  # Return List Item and Page object of current page


def setPaginationForItemsWithValues(items, *attr, page_num=10, page=1, fullAttrVal=False):
    '''
    Method  return List of Values of items and  Pagination
    items = QuerySet of items
    attr = (list of item's attributes)
    page = number of current page
    page_num = num element per page
    '''
    paginator = Paginator(items, page_num)

    try:
        page = items = paginator.page(page)
    except Exception:
        page = items = paginator.page(1)

    if not isinstance(items, list):
        items = tuple([item.pk for item in page.object_list])

    attributeValues = Item.getItemsAttributesValues(attr, items, fullAttrVal)

    return attributeValues, page  # Return List Item and Page object of current page


def getItemsListWithPagination(cls, *attr, page=1, site=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''

    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if site:
        items = clsObj.active.get_active().filter(sites__id=settings.SITE_ID)
    else:
        items = clsObj.active.get_active().all()

    paginator = Paginator(items, 10)
    try:
        page = items = paginator.page(page)  # check if page is valid
    except Exception:
        page = items = paginator.page(1)

    items = tuple([item.pk for item in page.object_list])
    attributeValues = clsObj.getItemsAttributesValues(attr, items)

    return attributeValues, page  # Return List Item and Page object of current page


def getItemsList(cls, *attr, qty=None, site=False, fullAttrVal=False):
    '''
    Method  return List of Item of specific class including Pagination
    cls = (class name of specific Item (News , Company))
    attr = (list of item's attributes)
    page = number of current page
    '''

    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if site:
        items = clsObj.active.get_active().filter(sites__id=settings.SITE_ID)[:qty]
    else:
        items = clsObj.active.get_active().all()[:qty]

    items = tuple([item.pk for item in items])
    attributeValues = clsObj.getItemsAttributesValues(attr, items, fullAttrVal=fullAttrVal)

    return attributeValues


# Deprecated
def sortByAttr(cls, attribute, order="ASC", type="str"):  # IMPORTANT: should be called before any filter
    '''
        Order Items by attribute
        cls: class name instance of Item
        attribute: Attribute name
        order: Order direction DESC / ASC
        type: Sorting type str/int
            Example: qSet = sortByAtt("Product", "NAME")
            Example: qSet = sortByAtt("Product", "NAME", "DESC", "int")
    '''

    clsObj = (globals()[cls])

    if not issubclass(clsObj, Item):
        raise ValueError("Wrong object type")

    if type != "str":
        case = 'TO_NUMBER("CORE_VALUE"."TITLE", \'999999999.999\')'
    else:
        case = 'CAST("CORE_VALUE"."TITLE" AS VARCHAR(100))'

    if order != "ASC":
        case = '-' + case

    return clsObj.active.get_active().filter(item2value__attr__title=attribute).extra(order_by=[case])


def sortQuerySetByAttr(queryset, attribute, order="ASC", type="str"):  # IMPORTANT: should be called before any filter
    '''
        Order Items by attribute
        cls: class name instance of Item
        attribute: Attribute name
        order: Order direction DESC / ASC
        type: Sorting type str/int
            Example: qSet = sortByAtt("Product", "NAME")
            Example: qSet = sortByAtt("Product", "NAME", "DESC", "int")
    '''

    if type != "str":
        case = 'TO_NUMBER("CORE_VALUE"."TITLE", \'999999999.999\')'
    else:
        case = 'CAST("CORE_VALUE"."TITLE" AS VARCHAR(100))'

    if order != "ASC":
        case = '-' + case

    return queryset.model.objects.filter(pk__in=queryset, item2value__attr__title=attribute).extra(order_by=[case])


def currencySymbol(currency):
    if not currency:
        return ""

    symbols = {
        'EUR': '€',
        'USD': '$',
        'NIS': '₪',
    }

    return symbols.get(currency.upper(), currency)


def _setCouponsStructure(couponsDict):
    for item, attrs in couponsDict.items():

        if 'COST' not in attrs or 'COUPON_DISCOUNT' not in attrs:
            raise ValueError('Attributes COST and COUPON_DISCOUNT are required')

        newDict = copy(attrs)

        for attr, values in newDict.items():
            if attr == 'title':
                continue

            if attr == "COUPON_DISCOUNT":
                discount = values[0]

                if not isinstance(discount, dict):
                    raise ValueError('You should pass full attribute data')

                couponsDict[item][attr + '_END_DATE'] = discount['end_date']
                couponsDict[item][attr] = discount['title']
            else:
                couponsDict[item][attr] = values[0]['title']

    return couponsDict


# Deprecated
def _setProductStructure(prodDict):
    for item, attrs in prodDict.items():

        if 'COST' not in attrs or 'DISCOUNT' not in attrs:
            raise ValueError('Attributes COST and DISCOUNT are required')

        newDict = copy(attrs)

        for attr, values in newDict.items():
            if attr == 'title':
                continue

            if attr == "DISCOUNT":
                discount = values[0]

                price = float(newDict['COST'][0])
                prodDict[item]['DISCOUNT_COST'] = price - (price * float(discount)) / 100
                prodDict[item]['COST_DIFFERENCE'] = price - prodDict[item]['DISCOUNT_COST']
                prodDict[item]['COST_DIFFERENCE'] = '{0:,.0f}'.format(prodDict[item]['COST_DIFFERENCE'])
                prodDict[item]['DISCOUNT_COST'] = '{0:,.2f}'.format(prodDict[item]['DISCOUNT_COST'])
                prodDict[item][attr] = discount
            elif attr == "COST":
                prodDict[item]['COST'] = '{0:,.2f}'.format(float(newDict['COST'][0]))
            elif attr == "CURRENCY":
                prodDict[item][attr] = values[0]['title']
                prodDict[item][attr + '_SYMBOL'] = currencySymbol(prodDict[item][attr])
            else:
                prodDict[item][attr] = values[0]

    return prodDict


def setStructureForHiearhy(dictinory, items):
    '''
      Method get hierarchy tree and list items with attribute NAME
      and build structure of object
      Example of usage:
       hierarchyStructure = Category.hierarchy.getTree(10)
       categories_id = [cat['ID'] for cat in hierarchyStructure]
       categories = Item.getItemsAttributesValues(("NAME",), categories_id)
       dictStructured = func.setStructureForHiearhy(hierarchyStructure, categories)
       will return :
      {
          {PARENT1}:
                  {PARENT1:item,
                  Child1:item},
           {PARENT2}:
                  {PARENT2:item,
                  Child1:item,
                  Child2:item},
      }


    '''
    level = 0
    dictStructured = {}

    for node in dictinory:
        if node['LEVEL'] == 1:
            nameOfList = items[node['ID']]['NAME'][0].strip()
            dictStructured[nameOfList] = {}
            node['item'] = items[node['ID']]
            dictStructured[nameOfList]['@Parent'] = node
        else:
            node['pre_level'] = level
            node['item'] = items[node['ID']]
            node['parent_item'] = items[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
            level = node['LEVEL']
            dictStructured[nameOfList][items[node['ID']]['NAME'][0].strip()] = node

    return dictStructured


def getCountofSepecificItemsRelated(childCls, list, filterChild=None):
    '''
        Get count of some type of child for list of some type of parents parents
            "childCls" - Type / Class of child objects
            "list" - iterable list of parent ids

                Example: getCountofSepecificRelatedItems("Product", [1, 2], "Category")
                #will return number of products in categories with id 1 and 2

                returns: [{
                    'parent': 1,
                    'childCount': 4
                }, {
                    'parent': 2,
                    'childCount': 2
                }]
    '''
    clsObj = (globals()[childCls])

    if filterChild is None:
        filterChild = F(clsObj._meta.model_name)

    return Item.objects.filter(c2p__parent__in=list, c2p__child=filterChild, c2p__type="relation") \
        .values('c2p__parent').annotate(childCount=Count('c2p__parent'))


def _categoryStructure(categories, listCount, catWithAttr, needed=None):
    elCount = {}
    parent = 0

    if len(listCount) == 0:
        return {}

    keys = list(listCount[0].keys())
    childKey = 'childCount'

    parentKey = keys[1]

    if childKey == parentKey:
        parentKey = keys[0]

    if needed is not None:
        for cat in catWithAttr:
            if cat not in needed:
                del catWithAttr[cat]

    for dictCount in listCount:
        elCount[dictCount[parentKey]] = dictCount[childKey]

    for cat in categories:

        if cat['LEVEL'] == categories[0]['LEVEL']:
            parent = cat['ID']

        if 'count' not in catWithAttr[parent]:
            catWithAttr[parent]['count'] = elCount.get(cat['ID'], 0)
        else:
            catWithAttr[parent]['count'] += elCount.get(cat['ID'], 0)

    return catWithAttr


def resize(img, box, fit, out):
    '''Downsample the image.
        @param img: Image -  an Image-object
        @param box: tuple(x, y) - the bounding box of the result image
        @param fit: boolean - crop the image to fill the box
        @param out: file-like-object - save the image into the output stream
        '''
    # preresize image with factor 2, 4, 8 and fast algorithm

    img = Image.open(img)

    factor = 1
    while img.size[0] / factor > 2 * box[0] and img.size[1] / factor > 2 * box[1]:
        factor *= 2
    if factor > 1:
        img.thumbnail((img.size[0] / factor, img.size[1] / factor), Image.NEAREST)

    # calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2 / box[0]
        hRatio = 1.0 * y2 / box[1]
        if hRatio > wRatio:
            y1 = int(y2 / 2 - box[1] * wRatio / 2)
            y2 = int(y2 / 2 + box[1] * wRatio / 2)
        else:
            x1 = int(x2 / 2 - box[0] * hRatio / 2)
            x2 = int(x2 / 2 + box[0] * hRatio / 2)
        img = img.crop((x1, y1, x2, y2))

    # Resize the image with best quality algorithm ANTI-ALIAS
    img.thumbnail(box, Image.ANTIALIAS)

    if img.mode == "CMYK":
        img = img.convert("RGB")

    # save it into a file-like object
    img.save(out, "PNG", quality=95)


def findKeywords(tosearch):
    '''
        Automatically find seo keyword on each text using python libraries

        str tosearch - Text to find keywords
    '''

    import string
    import difflib

    exclude = set(string.punctuation)
    exclude.remove('-')
    tosearch = ''.join(ch for ch in tosearch if ch not in exclude and (ch.strip() != '' or ch == ' '))
    words = [word.lower() for word in tosearch.split(" ") if 3 <= len(word) <= 20 and word.isdigit() is False][:30]

    length = len(words)
    keywords = []

    for word in words:
        if len(difflib.get_close_matches(word, keywords)) > 0:
            continue

        count = len(difflib.get_close_matches(word, words))

        precent = (count * length) / 100

        if 2.5 <= precent <= 3:
            keywords.append(word)

        if len(keywords) > 5:
            break

    if len(keywords) < 3:
        for word in words:
            if len(difflib.get_close_matches(word, keywords)) == 0:
                keywords.append(word)

                if len(keywords) == 3:
                    break

    return ' '.join(keywords)


def notify(message_type, notificationtype, **params):
    '''

    '''
    user = params['user']
    params['user'] = user.pk
    message = SystemMessages.objects.get(type=message_type)
    notif = Notification(user=user, message=message, create_user=user)
    notif.save()

    publish_realtime(notificationtype, **params)


def publish_realtime(publication_type, **params):
    import redis
    from django.conf import settings
    import json

    ORDERS_FREE_LOCK_TIME = getattr(settings, 'ORDERS_FREE_LOCK_TIME', 0)
    ORDERS_REDIS_HOST = getattr(settings, 'ORDERS_REDIS_HOST', 'localhost')
    ORDERS_REDIS_PORT = getattr(settings, 'ORDERS_REDIS_PORT', 6379)
    ORDERS_REDIS_PASSWORD = getattr(settings, 'ORDERS_REDIS_PASSWORD', None)
    ORDERS_REDIS_DB = getattr(settings, 'ORDERS_REDIS_DB', 0)

    # опять удобства
    service_queue = redis.StrictRedis(
        host=ORDERS_REDIS_HOST,
        port=ORDERS_REDIS_PORT,
        db=ORDERS_REDIS_DB,
        password=ORDERS_REDIS_PASSWORD
    ).publish

    service_queue(publication_type, json.dumps(params))


def getAnalytic(params=None):
    from appl.analytic.analytic import get_results

    if not isinstance(params, dict):
        raise ValueError('Filter required')

    if 'end_date' not in params:
        params['end_date'] = '2050-01-01'
    if 'start_date' not in params:
        params['start_date'] = '2014-01-01'

    params['metrics'] = 'ga:visitors'

    return get_results(**params)


def addDictinoryWithCountryToVacancy(vacancy_ids, vacancyList):
    countries = Country.objects.filter(p2c__child__p2c__child__p2c__child__p2c__child__in=vacancy_ids).distinct() \
        .values('pk', 'p2c__child__p2c__child__p2c__child__p2c__child')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)
    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child__p2c__child__p2c__child__p2c__child']] = country['pk']

    for id, vacancy in vacancyList.items():
        toUpdate = {
            'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
            'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
            'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id, 0) else [0],
            'COUNTRY_ID': country_dict.get(id, 0)
        }

        vacancy.update(toUpdate)

    return vacancyList


def addDictinoryWithCountryAndOrganization(ids, itemList):
    org_models = [Tpp.__name__.lower(), Company.__name__.lower()]

    countries = Country.objects.filter(p2c__child__contentType__model__in=org_models, p2c__child__p2c__child__in=ids,
                                       p2c__child__p2c__type='dependence').values('p2c__child__p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)

    organizations = Organization.objects.filter(p2c__child__in=ids, p2c__type='dependence').values('p2c__child', 'pk')
    organizations_ids = [organization['pk'] for organization in organizations]
    organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'SLUG'), organizations_ids)
    organizations_dict = {}

    for organization in organizations:
        organizations_dict[organization['p2c__child']] = organization['pk']

    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, item in itemList.items():
        if country_dict.get(id, False):
            toUpdate = {
                'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, [0]) else [0],
                'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, [0]) else [0],
                'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id,
                                                                                                           [0]) else [
                    0],
                'COUNTRY_ID': country_dict.get(id, 0)
            }

            item.update(toUpdate)

        if organizations_dict.get(id, False):
            if organizationIsCompany(id):
                url = 'companies:detail'
            else:
                url = 'tpp:detail'

            toUpdate = {
                'ORGANIZATION_FLAG': organizationsList[organizations_dict[id]].get('FLAG',
                                                                                   [0]) if organizations_dict.get(id, [
                    0]) else [0],
                'ORGANIZATION_NAME': organizationsList[organizations_dict[id]].get('NAME',
                                                                                   [0]) if organizations_dict.get(id, [
                    0]) else [0],
                'ORGANIZATION_SLUG': organizationsList[organizations_dict[id]].get('SLUG',
                                                                                   [0]) if organizations_dict.get(id, [
                    0]) else [0],
                'ORGANIZATION_ID': organizations_dict.get(id, 0),
                'ORGANIZATION_URL': url
            }

            item.update(toUpdate)


def addDictinoryWithCountryAndOrganizationToInnov(ids, itemList):
    cabinets = Cabinet.objects.filter(p2c__child__in=ids).values('p2c__child', 'pk')

    cabinets_ids = [cabinet['pk'] for cabinet in cabinets]
    countries = Country.objects.filter(p2c__child__in=cabinets_ids).values('p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)

    country_dict = {}

    for country in countries:
        if country['pk']:
            country_dict[country['p2c__child']] = country['pk']

    cabinetList = Item.getItemsAttributesValues(("USER_FIRST_NAME", 'USER_LAST_NAME'), cabinets_ids)

    cabinets_dict = {}

    for cabinet in cabinets:
        cabinets_dict[cabinet['p2c__child']] = {
            'CABINET_NAME': cabinetList[cabinet['pk']].get('USER_FIRST_NAME', 0) if cabinetList.get(cabinet['pk'],
                                                                                                    0) else [0],
            'CABINET_LAST_NAME': cabinetList[cabinet['pk']].get('USER_LAST_NAME', 0) if cabinetList.get(cabinet['pk'],
                                                                                                        0) else [0],
            'CABINET_ID': cabinet['pk'],
            'CABINET_COUNTRY_NAME': countriesList[country_dict[cabinet['pk']]].get('NAME', [0]) if country_dict.get(
                cabinet['pk'], False) else [0],
            'CABINET_COUNTRY_FLAG': countriesList[country_dict[cabinet['pk']]].get('FLAG', [0]) if country_dict.get(
                cabinet['pk'], False) else [0],
            'CABINET_COUNTRY_FLAG_CLASS': countriesList[country_dict[cabinet['pk']]].get('COUNTRY_FLAG',
                                                                                         [0]) if country_dict.get(
                cabinet['pk'], False) else [0],
            'CABINET_COUNTRY_ID': country_dict.get(cabinet['pk'], "")
        }

    addDictinoryWithCountryAndOrganization(ids, itemList)

    for id, innov in itemList.items():
        if cabinets_dict.get(id, 0):
            innov.update(cabinets_dict.get(id, 0))


def addDictinoryWithCountryToCompany(ids, itemList, add_organization=False):
    countries = Country.objects.filter(p2c__child__in=ids, p2c__type='dependence').values('p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)
    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child']] = country['pk']

    organizations = Organization.objects.filter(p2c__child__in=ids, p2c__type='relation').values('p2c__child', 'pk')

    organizations_ids = [organization['pk'] for organization in organizations]
    organizationsList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'SLUG'), organizations_ids)
    organizations_dict = {}

    for organization in organizations:
        organizations_dict[organization['p2c__child']] = organization['pk']

    for id, company in itemList.items():
        toUpdate = {
            'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
            'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
            'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id, [0]) else [
                0],
            'COUNTRY_ID': country_dict.get(id, 0)}
        try:
            company.update(toUpdate)
        except Exception as e:
            print('Passed Company ID:' + id + 'has not attribute list. The reason is:' + str(
                e) + 'Please, rebuild index.')
            pass

        if add_organization:
            if organizations_dict.get(id, False):
                if organizationIsCompany(id):
                    url = 'companies:detail'
                else:
                    url = 'tpp:detail'

                toUpdate = {
                    'ORGANIZATION_FLAG': organizationsList[organizations_dict[id]].get('FLAG',
                                                                                       [0]) if organizations_dict.get(
                        id, [0]) else [0],
                    'ORGANIZATION_NAME': organizationsList[organizations_dict[id]].get('NAME',
                                                                                       [0]) if organizations_dict.get(
                        id, [0]) else [0],
                    'ORGANIZATION_SLUG': organizationsList[organizations_dict[id]].get('SLUG',
                                                                                       [0]) if organizations_dict.get(
                        id, [0]) else [0],
                    'ORGANIZATION_ID': organizations_dict.get(id, 0),
                    'ORGANIZATION_URL': url
                }

                company.update(toUpdate)


def addToItemDictinoryWithCountryAndOrganization(id, itemList, withContacts=False):
    org_models = [Tpp.__name__.lower(), Company.__name__.lower()]

    countries = Country.objects.filter(p2c__child__contentType__model__in=org_models,
                                       p2c__child__p2c__type='dependence',
                                       p2c__child__p2c__child=id).values('p2c__child__p2c__child', 'pk')

    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG', 'COUNTRY_FLAG'), countries_id)

    organizations = Organization.objects.filter(p2c__child=id, p2c__type='dependence').values('p2c__child', 'pk')
    organizations_ids = [organization['pk'] for organization in organizations]

    attr = ("NAME", 'FLAG', 'IMAGE', 'SLUG')

    if withContacts:
        attr = attr + ('EMAIL', 'SITE_NAME', 'ADDRESS', 'TELEPHONE_NUMBER', 'FAX')

    organizationsList = Item.getItemsAttributesValues(attr, organizations_ids)
    organizations_dict = {}

    for organization in organizations:
        organizations_dict[organization['p2c__child']] = organization['pk']

    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    if country_dict.get(id, False):
        toUpdate = {
            'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
            'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
            'FLAG_CLASS': countriesList[country_dict[id]].get('COUNTRY_FLAG', [0]) if country_dict.get(id, 0) else [0],
            'COUNTRY_ID': country_dict.get(id, 0)
        }

        itemList.update(toUpdate)

    if organizations_dict.get(id, False):

        if organizationIsCompany(id):
            url = 'companies:detail'
        else:
            url = 'tpp:detail'

        toUpdate = {
            'ORGANIZATION_FLAG': organizationsList[organizations_dict[id]].get('FLAG', [0]) if organizations_dict.get(
                id, 0) else [0],
            'ORGANIZATION_NAME': organizationsList[organizations_dict[id]].get('NAME', [0]) if organizations_dict.get(
                id, 0) else [0],
            'ORGANIZATION_IMAGE': organizationsList[organizations_dict[id]].get('IMAGE', [0]) if organizations_dict.get(
                id, 0) else [0],
            'ORGANIZATION_SLUG': organizationsList[organizations_dict[id]].get('SLUG', [0]) if organizations_dict.get(
                id, [0]) else [0],
            'ORGANIZATION_EMAIL': organizationsList[organizations_dict[id]].get('EMAIL',
                                                                                [""]) if organizations_dict.get(id, [
                0]) else [0],
            'ORGANIZATION_SITE_NAME': organizationsList[organizations_dict[id]].get('SITE_NAME',
                                                                                    [""]) if organizations_dict.get(id,
                                                                                                                    [
                                                                                                                        0]) else [
                0],
            'ORGANIZATION_ADDRESS': organizationsList[organizations_dict[id]].get('ADDRESS',
                                                                                  [""]) if organizations_dict.get(id, [
                0]) else [0],
            'ORGANIZATION_TELEPHONE_NUMBER': organizationsList[organizations_dict[id]].get('FAX', [
                ""]) if organizations_dict.get(id, [0]) else [0],
            'ORGANIZATION_FAX': organizationsList[organizations_dict[id]].get('FAX', [""]) if organizations_dict.get(id,
                                                                                                                     [
                                                                                                                         0]) else [
                0],
            'ORGANIZATION_ID': organizations_dict.get(id, 0),
            'ORGANIZATION_URL': url
        }

        itemList.update(toUpdate)


def organizationIsCompany(item_id):
    if Company.objects.filter(p2c__child=item_id, p2c__type='dependence').exists():
        return True

    return False


def filter_live(request, model_name=None):
    """
        Converting GET request filter parameters (from popup window) to filter parameter for SearchQuerySet filter

        obj request - request context
    """

    if model_name:
        if request.GET and not request.session.get(model_name, False):
            request.session[model_name] = request.GET.urlencode()
            getParameters = QueryDict(request.session.get(model_name, False))
        elif len(request.GET) > 1 and request.GET.urlencode() != request.session.get(model_name, ""):
            if 'filter' in request.GET.urlencode():
                request.session[model_name] = request.GET.urlencode()
                getParameters = QueryDict(request.session.get(model_name, ""))
            else:
                del request.session[model_name]
                getParameters = QueryDict(request.session.get(model_name, ""))


        elif request.session.get(model_name, False):
            getParameters = QueryDict(request.session.get(model_name, False))
        else:
            getParameters = request.GET
    else:
        getParameters = request.GET

    searchFilter = []
    filtersIDs = {}
    filters = {}
    ids = []

    # allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch', 'bp_category']

    # get all filter parameters from request GET
    for name in filterList:
        filtersIDs[name] = []
        filters[name] = []

        for pk in getParameters.getlist('filter[' + name + '][]', []):
            try:
                filtersIDs[name].append(int(pk))
            except ValueError:
                continue

        ids += filtersIDs[name]

    # Do we have any valid filter ?
    if len(ids) > 0:
        attributes = Item.getItemsAttributesValues('NAME', ids)

        for pk, attr in attributes.items():
            # Creating a list of filter parameters

            if not isinstance(attr, dict) or 'NAME' not in attr or len(attr['NAME']) != 1:
                continue

            for name, id in filtersIDs.items():

                if pk in id:
                    filters[name].append({'id': pk, 'text': attr['NAME'][0]})

                newIDs = []
                # Security
                for i in id:
                    try:
                        newIDs.append(str(int(i)))
                    except ValueError:
                        continue

                if len(newIDs) > 0:
                    searchFilter.append('SQ(' + name + '__in =[' + ','.join(newIDs) + '])')

    if len(searchFilter) > 0:  # Converting a list of filter parameters to big "OR" filter
        searchFilter = eval(' | '.join(searchFilter))

    return filters, searchFilter


def getB2BcabinetValues(request):
    if request.user.is_authenticated():
        user = request.user
        cabinet = Cabinet.objects.get(user=user.pk)

        try:
            country = Country.objects.get(p2c__child=cabinet)
            country = country.getAttributeValues('NAME')
        except Exception:
            country = ""
        cabinetValues = {}
        cabinetValues['EMAIL'] = [user.email]
        cabinetValues['LOGIN'] = [user.username]
        cabinetValues.update(
            cabinet.getAttributeValues('PROFESSION', 'MOBILE_NUMBER', 'BIRTHDAY', 'PERSONAL_STATUS', 'SEX',
                                       'SKYPE', 'SITE_NAME', 'ICQ', 'USER_MIDDLE_NAME', 'USER_FIRST_NAME',
                                       'USER_LAST_NAME', 'IMAGE', 'TELEPHONE_NUMBER'))
        cabinetValues['COUNTRY'] = country

        return cabinetValues

    return None


def get_banner(block, site_id, filter_adv=None):
    # TODO optimize the function for batch
    banner_queryset = Banner.objects.filter(
        block__code=block,
        is_active=True,
        site=site_id,
        dates__contains=now().date()
    )
    targeting_filter = None

    for target_model, target_items in filter_adv.items():
        if not target_items:
            continue

        tmp_filter = Q(
            targets__content_type__model=target_model.lower(),
            targets__object_id__in=target_items
        )

        targeting_filter = tmp_filter if targeting_filter is None else targeting_filter | tmp_filter

    if targeting_filter is not None:
        banner_queryset = banner_queryset.filter(targeting_filter)

    return banner_queryset.order_by('?').first()


def get_tops(filterAdv=None):
    '''
        Get context advertisement items depended on received filter

        dict filterAdv - advertisement filter , can include countries organizations or branches
                (get it from getDeatailAdv() or getListAdv() )
    '''

    models = {
        Chamber: {
            'count': 1,  # Limit of this type to fetch
            'text': _('Organizations'),  # Title
            'detailUrl': 'tpp:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['countries']
        },
        News: {
            'count': 1,  # Limit of this type to fetch
            'text': _('News'),  # Title
            'detailUrl': 'news:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        },
        B2BProduct: {
            'count': 1,  # Limit of this type to fetch
            'text': _('Products'),  # Title
            'detailUrl': 'products:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['company', 'company__countries']
        },
        InnovationProject: {
            'count': 1,
            'text': _('Innovation Projects'),
            'detailUrl': 'innov:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['organization', 'organization__countries']
        },
        Company: {
            'count': 1,
            'text': _('Companies'),
            'detailUrl': 'companies:detail',  # URL namespace to detail page of this type of item
            'select_related': None,
            'prefetch_related': ['countries']
        },
        BusinessProposal: {
            'count': 1,
            'text': _('Business Proposals'),
            'detailUrl': 'proposal:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        },
        Requirement: {
            'count': 3,
            'text': _('Job requirements'),
            'detailUrl': 'vacancy:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['vacancy__department__organization', 'vacancy__department__organization__countries']
        },
        Exhibition: {
            'count': 1,
            'text': _('Exhibitions'),
            'detailUrl': 'exhibitions:detail',  # URL namespace to detail page of this type of item
            'select_related': ['country'],
            'prefetch_related': ['organization', 'organization__countries']
        }

    }

    for model, modelDict in models.items():
        # Get all active context advertisement of some specific type
        queryset = model.objects.filter(
            context_advertisements__is_active=True,
            context_advertisements__content_type__model=model.__name__.lower(),
            context_advertisements__dates__contains=now().date()
        )

        targeting_filter = None

        # Do we have some filters depended on current page ?
        for target_model, target_items in filterAdv.items():
            if not target_items:
                continue

            tmp_filter = Q(
                context_advertisements__targets__content_type__model=target_model.lower(),
                context_advertisements__targets__object_id__in=target_items
            )

            targeting_filter = tmp_filter if targeting_filter is None else targeting_filter | tmp_filter

        if targeting_filter is not None:
            queryset = queryset.filter(targeting_filter)

        if modelDict['select_related'] is not None:
            queryset = queryset.select_related(*modelDict['select_related'])

        if modelDict['prefetch_related'] is not None:
            queryset = queryset.prefetch_related(*modelDict['prefetch_related'])

        modelDict['queryset'] = queryset.order_by('?')[:int(modelDict['count'])]

    return models


def get_detail_adv_filter(obj):
    cache_key = "adv_filter:detail:%s:%s" % (obj.__class__, obj.pk)
    filter_by_model = cache.get(cache_key)

    if not filter_by_model:
        filter_by_model = {}

        org = getattr(obj, 'organization', None)
        company = getattr(obj, 'company', None) if not isinstance(obj, Organization) else None
        branches = getattr(obj, 'branches', None)

        if org is not None:
            if isinstance(org, Chamber):
                filter_by_model[Chamber.__name__] = [org.id]
            elif org.parent_id:
                filter_by_model[Chamber.__name__] = [org.parent_id]
        elif company:
            filter_by_model[Branch.__name__] = list(company.branches.all().values_list('pk', flat=True))

            if company.parent_id:
                filter_by_model[Chamber.__name__] = [company.parent_id]


        if branches is not None:
            if Branch.__name__ in filter_by_model:
                filter_by_model[Branch.__name__] += list(branches.all().values_list('pk', flat=True))
            else:
                filter_by_model[Branch.__name__] = list(branches.all().values_list('pk', flat=True))

        cache.set(cache_key, filter_by_model, 60 * 1)

    return filter_by_model


def get_list_adv_filter(request):
    cache_key = "adv_filter:list:%s" % hashlib.md5(request.META['QUERY_STRING'].encode('utf-8')).hexdigest()
    list_filter = cache.get(cache_key)

    if not list_filter:
        filter_by_model = {
            'chamber': [Chamber.__name__, []],
            'country': [Country.__name__, []],
            'branches': [Branch.__name__, []],
        }

        countries = []

        for filter_key, filter_items in filter_by_model.items():
            for pk in request.GET.getlist('filter[' + filter_key + '][]', []):
                try:
                    filter_items[1].append(int(pk))
                except ValueError:
                    continue

            # Add filter of countries of each tpp
            if filter_items[0] == Chamber.__name__ and len(filter_items[1]) > 0:
                countries + list(Country.objects \
                                 .filter(organizations__pk__in=filter_items[1]).values_list('pk', flat=True))

        filter_by_model['country'][1] += countries
        list_filter = dict(filter_by_model.values())
        cache.set(cache_key, filter_by_model, 60 * 5)

    return list_filter


def getActiveSQS():
    '''
        Get active items from search indexes
    '''
    return SearchQuerySet().filter(
        SQ(obj_end_date__gt=timezone.now()) | SQ(obj_end_date__exact=datetime.datetime(1, 1, 1)),
        obj_start_date__lt=timezone.now())


def emptyCompany():
    template = loader.get_template('permissionDen.html')
    request = get_request()
    context = RequestContext(request, {})
    page = template.render(context)
    return page


def permissionDenied(message=_('Sorry but you cannot modify this item ')):
    template = loader.get_template('permissionDenied.html')
    request = get_request()
    context = RequestContext(request, {'message': message})
    page = template.render(context)
    return page


def clean_from_html(value):
    if len(value) > 0:
        document = lxml.html.document_fromstring(value)
        raw_text = document.text_content()
        return raw_text
    else:
        return ""


def getUserPermsForObjectsList(user, obj_lst, obj_model_name):
    '''
        Receive User, list of Items PK obj_lst and model name of these Items obj_model_name, for example, "Product".
        Returns dictionary with list of permissions for current user for each object instance.
        Example:    user = User.objects.get(pk=1)
                    getUserPermsForObjectsList(user, [1, 2, 34, 67], 'Product')
        Return:
        {
            '1': ['add_product', 'change_product', 'read_product', 'delete_product'],
            '2': ['add_product', 'read_product'],
            '34': ['read_product'],
            '67': ['add_product', 'change_product', 'read_product', 'delete_product']
        }
    '''
    if len(obj_lst) == 0:
        return {}

    perms_dict = {}

    if isinstance(obj_lst[0], (int, str)):
        items = (globals()[obj_model_name]).objects.filter(pk__in=obj_lst)
    else:
        items = obj_lst

    for itm in items:
        perms_dict[str(itm.pk)] = itm.getItemInstPermList(user)

    return perms_dict


def cachePisibility(request):
    '''
        Check if need to cache the page
    '''

    q = request.GET.get('q', '')
    query = request.GET.urlencode()

    if not request.user.is_authenticated() and query.find('sortField') == -1 and query.find('order') == -1 and \
                    query.find('filter') == -1 and q == '':
        return True

    return False


def show_toolbar(request):
    if request.user.is_authenticated():
        if request.user.is_superuser:
            return True

    return False


def make_object_dates_aware(obj):
    timezoneInfo = get_current_timezone()

    if obj.end_date and is_naive(obj.end_date):
        obj.end_date = make_aware(obj.end_date, timezoneInfo)
        obj.save()

    if obj.start_date and is_naive(obj.start_date):
        obj.start_date = make_aware(obj.start_date, timezoneInfo)
        obj.save()

    return obj


def autocomplete_filter(filter_key, q, page):
    filters = {
        'country': {
            'model': Country,
            'index_model': CountryIndex,
        },
        'chamber': {
            'model': Chamber,
            'index_model': ChamberIndex,
        },
        'branches': {
            'model': Branch,
            'index_model': BranchIndex,
        },
        'b2b_categories': {
            'model': B2BProductCategory,
            'index_model': B2bProductCategoryIndex,
        },
        'bp_categories': {
            'model': BusinessProposalCategory,
            'index_model': BusinessProposalCategoryIndex,
        }
    }

    model_dict = filters.get(filter_key, None)

    if model_dict is None:
        return None

    if (len(q) != 0 and len(q) <= 2) or page < 0:
        return None

    if len(q) > 2:
        s = SearchEngine(doc_type=model_dict['index_model']).query('match', name_auto=q)
        fields = [field.name for field in model_dict['model']._meta.get_fields()]

        if 'is_active' in fields:
            s = s.query('match', is_active=True)

        if 'is_deleted' in fields:
            s = s.query('match', is_deleted=False)

        paginator = Paginator(s, 10)
        hits = paginator.page(page).object_list.execute().hits
        object_ids = [obj.django_id for obj in hits]

        return model_dict['model'].objects.filter(pk__in=object_ids), hits.total
    else:
        objects = model_dict['model'].objects.all()
        paginator = Paginator(objects, 10)

        return paginator.page(page).object_list, paginator.count


def getItemMeta(request, itemAttributes):
    image = ''

    if itemAttributes.get('IMAGE', [''])[0]:
        image = settings.MEDIA_URL + 'original/' + itemAttributes.get('IMAGE', [''])[0]

    url = urlparse(request.build_absolute_uri())

    return {
        'title': Truncator(itemAttributes.get('NAME', [''])[0]).chars("80", truncate='...'),
        'image': image,
        'url': url.scheme + "://" + url.netloc + url.path,
        'text': itemAttributes.get('DETAIL_TEXT', [''])[0]
    }


def get_countrys_for_sqs_objects(object_list):
    countries = []

    for obj in object_list:
        country = getattr(obj, 'country', False)

        if not country:
            continue

        if isinstance(country, list):
            if len(country) != 1:
                continue
            else:
                country = country[0]

        countries.append(country)

    if len(countries) > 0:
        countryDict = {}
        new_object_list = []

        for country in SearchQuerySet().models(Country).filter(django_id__in=countries):
            countryDict[int(country.pk)] = country

        if len(countryDict) > 0:
            for obj in object_list:
                country = getattr(obj, 'country', None)

                if not country:
                    new_object_list.append(obj)
                    continue

                if isinstance(country, list):
                    if len(country) == 1:
                        country = int(country[0])
                    else:
                        new_object_list.append(obj)
                        continue

                if country not in countryDict:
                    new_object_list.append(obj)
                    continue

                obj.country = countryDict[int(country)]
                new_object_list.append(obj)

            return new_object_list

    return object_list


def get_organization_for_objects(object_list):
    orgs = []

    for obj in object_list:

        company = getattr(obj, 'company', False)
        tpp = getattr(obj, 'tpp', False)

        if company:
            orgs.append(company)
        elif tpp:
            orgs.append(tpp)

    if len(orgs) > 0:
        orgDict = {}

        for org in SearchQuerySet().models(Company, Tpp).filter(django_id__in=orgs):
            orgDict[int(org.pk)] = org

        if len(orgDict) > 0:
            new_object_list = []

            for obj in object_list:
                company = getattr(obj, 'company', False)
                tpp = getattr(obj, 'tpp', False)

                if company:
                    if company in orgDict:
                        orgDict[company].__setattr__('url', 'companies:detail')
                        obj.__setattr__('organization', orgDict[company])
                elif tpp:
                    if tpp in orgDict:
                        orgDict[tpp].__setattr__('url', 'tpp:detail')
                        obj.__setattr__('organization', orgDict[tpp])

                new_object_list.append(obj)

            return new_object_list

    return object_list


def get_cabinet_data_for_objects(object_list):
    new_object_list = []

    for obj in object_list:
        if obj.cabinet:
            obj.__setattr__('cabinet', SearchQuerySet().models(Cabinet).filter(django_id=obj.cabinet))
        new_object_list.append(obj)

    return new_object_list


def get_categories_data_for_products(object_list):
    new_object_list = []

    for obj in object_list:
        obj.__setattr__('categories', SearchQuerySet().models(Category).filter(django_id__in=obj.categories))
        new_object_list.append(obj)

    return new_object_list
