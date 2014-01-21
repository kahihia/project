from django.shortcuts import render
from django.shortcuts import render_to_response

from appl.models import News, Category, Country, Tpp, Review ,Product

from core.models import Value, Item, Attribute, Dictionary , Relationship
from django.db.models import Count
from appl import func

from django.conf import settings

def home(request):

    newsList = func.getItemsList("News", "NAME", "IMAGE", qty=3)

    hierarchyStructure = Category.hierarchy.getTree()

    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)  # Select of categories
    hierarchyStructure = hierarchyStructure[:10]

    countryList = func.getItemsList("Country", "NAME")

    sortedHierarchyStructure = _sortMenu(hierarchyStructure) if len(hierarchyStructure) > 0 else {}
    level = 0
    for node in sortedHierarchyStructure:
        node['pre_level'] = level
        node['item'] = categories[node['ID']]
        node['parent_item'] = categories[node['PARENT_ID']] if node['PARENT_ID'] is not None else ""
        level = node['LEVEL']



    #TODO Jenya: Указывай более явно параметры
    tppList = func.getItemsList("Tpp", "NAME", "IMAGE")

    reviewList = func.getItemsList("Review", "NAME", "IMAGE", "Photo", qty=3)
    #get 3 active coupons ordered by end date
    couponsObj = Product.getCoupons().order_by('item2value__end_date')[:3]
    coupons_ids = [cat.pk for cat in couponsObj]

    coupons = Product.getItemsAttributesValues(("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE"), coupons_ids,
                                               fullAttrVal=True)

    coupons = func._setCouponsStructure(coupons)

    productsSale = func.sortByAttr("Product", "DISCOUNT", "DESC", "int")
    productsSale = Product.getProdWithDiscount(productsSale)[:15]

    productsSale_ids = [prod.pk for prod in productsSale]
    productsSale = Product.getItemsAttributesValues(("NAME", "DISCOUNT", "IMAGE", "COST"), productsSale_ids)
    productsSale = func._setProductStructure(productsSale)

    flagList = func.getItemsList("Country", "NAME", "FLAG")

    return render_to_response("index.html", locals())


def about(request):

    return render_to_response("About/About.html")

def set_news_list(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Anons", "DETAIL_TEXT", "IMAGE", page=page)

    itemsList = result[0]
    page = result[1]
    return render_to_response('NewsList.html', locals())


def _sortMenu(hierarchyStructure):
    sortedHierarchyStructure = []
    dictToSort = []
    id = hierarchyStructure[0]['ID']
    for i in range(0, len(hierarchyStructure)):
        if hierarchyStructure[i]["LEVEL"] == 1 and hierarchyStructure[i]['ID'] != id:
            id = hierarchyStructure[i]['ID']
            sortedHierarchyStructure.extend(_sortList(dictToSort))
            dictToSort = []

        dictToSort.append(hierarchyStructure[i])

    if len(dictToSort) > 0:
       sortedHierarchyStructure.extend(_sortList(dictToSort))

    return sortedHierarchyStructure

def _sortList(dict):
    sortedDict = []
    i = 0
    while i < len(dict):
        if dict[i]['LEVEL'] > 3:
            dict.pop(i)
            i-= 1
        if dict[i]['ISLEAF'] == 1 and dict[i]["LEVEL"] == 2:
            sortedDict.append(dict.pop(i))
            i -= 1
        i+=1

    dict.extend(sortedDict)
    return dict


