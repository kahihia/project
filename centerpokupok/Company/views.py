__author__ = 'user'
from core.models import Item
from appl.models import Company, Category, Product, Comment, Cabinet, Favorite
from django.shortcuts import render_to_response, get_object_or_404
from appl import func
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Count


def storeMain(request, company, category=None):

    companyObj = get_object_or_404(Company, pk=company)

    filter = {}

    if category:
        filter['c2p__parent_id'] = category

    #----NEW PRODUCT LIST -----#
    products = Product.getNew().filter(sites=settings.SITE_ID, c2p__parent_id=company).filter(**filter)[:4]
    products = [prd.pk for prd in products]
    newProducrList = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT', 'DISCOUNT'),
                                                      products)

    #----NEW PRODUCT LIST -----#
    products = Product.getTopSales().filter(sites=settings.SITE_ID)
    popular = products[:4]
    popular = [prd.pk for prd in popular]

    popular = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     popular)

    products = products.filter(c2p__parent_id=company).filter(**filter)[:4]
    products = [prd.pk for prd in products]

    topPoductList = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     products)

    #------ 3 Coupons ----------#
    couponsObj = Product.getCoupons().filter(sites=settings.SITE_ID, c2p__parent_id=company)\
                     .filter(**filter).order_by('item2value__end_date')[:3]

    coupons_ids = [cat.pk for cat in couponsObj]
    coupons = Product.getItemsAttributesValues(("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE"), coupons_ids,
                                               fullAttrVal=True)
    coupons = func._setCouponsStructure(coupons)

    #----------- Products with discount -------------#
    productsSale = Product.getProdWithDiscount().filter(sites=settings.SITE_ID, c2p__parent_id=company)\
                     .filter(**filter).order_by('item2value__end_date')

    productsSale = func.sortQuerySetByAttr(productsSale, "DISCOUNT", "DESC", "int")[:15]
    productsSale_ids = [prod.pk for prod in productsSale]
    productsSale = Product.getItemsAttributesValues(("NAME", "DISCOUNT", "IMAGE", "COST"), productsSale_ids)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr['IMAGE'][0]

    return render_to_response("Company/index.html", {'companyID': company, 'name': name, 'picture': picture,
                                                     'coupons': coupons,'productsSale': productsSale,
                                                     'newProducrList': newProducrList, 'topPoductList': topPoductList,
                                                     'popular': popular, 'menu': 'main',
                                                     'store_url': 'companies:category', 'user': request.user})

def about(request, company):
    companyObj = get_object_or_404(Company, pk=company)

    popular = Product.getTopSales().filter(sites=settings.SITE_ID)[:4]
    popular = [prd.pk for prd in popular]

    popular = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     popular)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE', 'DETAIL_TEXT')
    name = attr.get('NAME', [''])[0]
    picture = attr.get('IMAGE', [''])[0]
    detail_text = attr.get('DETAIL_TEXT', [''])[0]


    return render_to_response("Company/about.html", {'companyID': company, 'name': name, 'picture': picture,
                                                     'menu': 'about', 'detail_text': detail_text, 'popular': popular,
                                                     'user': request.user})

def contact(request, company):
    companyObj = get_object_or_404(Company, pk=company)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr['IMAGE'][0]

    return render_to_response("Company/contact.html", {'companyID': company, 'name': name, 'picture': picture,
                                                       'menu': 'contact', 'user': request.user})

def products(request, company, category=None, page=1):
    companyObj = get_object_or_404(Company, pk=company)
    filter = {}

    if category:
        categories = Category.hierarchy.getDescendants(category)
        category_ids = [cat['ID'] for cat in categories]
        filter['c2p__parent_id__in'] = category_ids

    products = Product.getNew().filter(sites=settings.SITE_ID, c2p__parent_id=company).filter(**filter)

    popular = Product.getTopSales().filter(sites=settings.SITE_ID)[:4]
    popular = [prd.pk for prd in popular]

    popular = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     popular)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr['IMAGE'][0]

    #-------------- Store Categories ---------------#
    storeCategories = companyObj.getStoreCategories()
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    root_cats = [cat['ID'] for cat in hierarchyStructure if cat['LEVEL'] == 1]
    categories = Item.getItemsAttributesValues(("NAME",), root_cats)

    storeCategories = func._categoryStructure(hierarchyStructure, storeCategories, categories)

    result = func.setPaginationForItemsWithValues(products, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                                 'DISCOUNT', 'COUPON_DISCOUNT', page_num=12, page=page)
    #Product list , with companies and countries
    products = result[0]
    products_ids = [key for key, value in products.items()]
    favorites_dict = {}
    if request.user.is_authenticated():
        favorites = Favorite.objects.filter(c2p__parent__cabinet__user=request.user, p2c__child__in=products_ids).values("p2c__child")
        for favorite in favorites:
            favorites_dict[favorite['p2c__child']] = 1


    comments = Comment.objects.filter(c2p__parent__in=products_ids).values("c2p__parent").annotate(num_comments=Count("c2p__parent"))
    comment_dict = {}
    for comment in comments:
        comment_dict[comment['c2p__parent']] = comment['num_comments']

    for id, product in products.items():
        toUpdate = {'COMMENTS': comment_dict.get(id, 0),
                    'FAVORITE': favorites_dict.get(id, 0)}
        product.update(toUpdate)
    #Paginator
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    if category:
        url_paginator = "companies:products_category_paged"
        url_parameter = [company, category]
    else:
        url_paginator = "companies:products_paged"
        url_parameter = [company]

    return render_to_response("Company/products.html", {'companyID': company, 'name': name, 'picture': picture,
                                                        'storeCategories': storeCategories, 'products': products,
                                                        'menu': 'products','store_url': 'companies:products_category',
                                                        'page': page, 'paginator_range': paginator_range,
                                                        'url_paginator': url_paginator, 'url_parameter':url_parameter,
                                                        'popular': popular, 'user': request.user})


def coupons(request, company, category=None, page=1):
    companyObj = get_object_or_404(Company, pk=company)

    filter = {}

    if category:
        categories = Category.hierarchy.getDescendants(category)
        category_ids = [cat['ID'] for cat in categories]
        filter['c2p__parent_id__in'] = category_ids

    coupons = Product.getCoupons()

    popular = Product.getTopSales().filter(sites=settings.SITE_ID)[:4]
    popular = [prd.pk for prd in popular]

    popular = Product.getItemsAttributesValues(("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT','DISCOUNT'),
                                                     popular)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr['IMAGE'][0]

    #-------------- Store Categories ---------------#
    storeCategories = companyObj.getStoreCategories(coupons)
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    root_cats = [cat['ID'] for cat in hierarchyStructure if cat['LEVEL'] == 1]
    categories = Item.getItemsAttributesValues(("NAME",), root_cats)

    storeCategories = func._categoryStructure(hierarchyStructure, storeCategories, categories)

    coupons = coupons.filter(sites=settings.SITE_ID, c2p__parent_id=company).filter(**filter)

    result = func.setPaginationForItemsWithValues(coupons, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                                 'DISCOUNT', 'COUPON_DISCOUNT', page_num=16, page=page, fullAttrVal=True)
    #Product list , with companies and countries
    coupons = result[0]
    coupons = func._setCouponsStructure(coupons)

    #Paginator
    page = result[1]
    paginator_range = func.getPaginatorRange(page)

    if category:
        url_paginator = "companies:coupons_category_paged"
        url_parameter = [company, category]
    else:
        url_paginator = "companies:coupons_paged"
        url_parameter = [company]

    return render_to_response("Company/coupons.html", {'companyID': company, 'name': name, 'picture': picture,
                                                       'storeCategories': storeCategories, 'menu': 'coupons',
                                                       'store_url': 'companies:coupons_category', 'page': page,
                                                       'paginator_range': paginator_range, 'url_paginator':url_paginator,
                                                       'url_parameter': url_parameter, 'coupons': coupons,
                                                       'popular': popular, 'user': request.user})