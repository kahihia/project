from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Category, Country, Product, Cabinet, Order, Favorite
from core.models import Value, Item, Attribute, Dictionary, User
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from centerpokupok.forms import UserDetail, OrderForm
from django.utils.translation import ugettext as _


@login_required(login_url=("/registration/"))
def get_profile(request):
    #Categories list in header
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

    #Counrty list in header
    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)
   #---Form for main data of ptofile ------#

    user = request.user
    #-------current url for Profile menu ----#
    curr_url = "main"
    succsefull_save = ""
    if request.POST:
        user_form = UserDetail(request.POST)
        if user_form.is_valid():
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.date_of_birth = user_form.cleaned_data['birthday']
            user.save()
            #----shown when prfile data successfully saved ------#
            succsefull_save = _("was successfully saved ")
    else:
        user_form = UserDetail(initial={"first_name": user.first_name, 'last_name': user.last_name,
                               "birthday": user.date_of_birth})


    return render_to_response("Cabinet/index.html", {'user_form': user_form, 'user': user,
                                                     'succsefull_save': succsefull_save, 'curr_url': curr_url,
                                                     'categotySelect': categotySelect, 'countryList': countryList},
                                                      context_instance=RequestContext(request))

@login_required(login_url=("/registration/"))
def get_shipping_detail(request):
     #Categories list in header
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

    #Counrty list in header
    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)
    #----form for shipping data in profile -----#
    user = request.user
    succsefull_save = ""
  #-------current url for Profile menu ----#
    curr_url = "shipping_address"
    if request.POST:
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            cabinet = get_object_or_404(Cabinet, user=user.pk)
            cabinet.setAttributeValue({'CITY': [order_form.cleaned_data['city']],
                                       'COUNTRY': [order_form.cleaned_data['country']],
                                       'ZIP': [order_form.cleaned_data['zipcode']],
                                       'ADDRESS': [order_form.cleaned_data['address']],
                                       'TELEPHONE_NUMBER': [order_form.cleaned_data['telephone_number']],
                                       'SHIPPING_NAME': [order_form.cleaned_data['recipient_name']]}, user)
           #----shown when prfile data successfully saved ------#
            succsefull_save = _("was successfully saved ")


    else:
        cabinet = get_object_or_404(Cabinet, user=user.pk)
        address = cabinet.getAttributeValues("CITY", "COUNTRY", "ZIP", "ADDRESS", "TELEPHONE_NUMBER", "SHIPPING_NAME")
        if not address:
            address = {}
        order_form = OrderForm(initial={'recipient_name': address['SHIPPING_NAME'][0] if address.get('SHIPPING_NAME', False) else "",
                                        'city': address['CITY'][0] if address.get('CITY', False) else "",
                                        'country': address['COUNTRY'][0] if address.get('COUNTRY', False) else "",
                                        'zipcode':address['ZIP'][0] if address.get('ZIP', False) else "",
                                        'address': address['ADDRESS'][0] if address.get('ADDRESS', False) else "",
                                        'telephone_number':address['TELEPHONE_NUMBER'][0] if address.get('TELEPHONE_NUMBER', False) else ""
                                        })


    return render_to_response("Cabinet/shippingAddress.html", {'order_form': order_form, 'user': user,
                                                               'succsefull_save': succsefull_save, 'curr_url': curr_url,
                                                               'categotySelect': categotySelect,
                                                               'countryList': countryList},
                                                                context_instance=RequestContext(request))
@login_required(login_url=("/registration/"))
def get_order_history(request, page=1):
    #------order history of user with pagination-----#

    #Categories list in header
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

    #Counrty list in header
    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)


    user = request.user
    curr_url = "order_history"
    cabinet = Cabinet.objects.filter(user=user)
    orders = Order.objects.filter(c2p__parent__in=cabinet).order_by("-pk")
    attr = ("IMAGE", 'NAME', 'CURRENCY', 'COST', 'QUANTITY', 'CITY', 'COUNTRY', 'ADDRESS')
    result = func.setPaginationForItemsWithValues(orders, *attr, page_num=5, page=page)
    orderList = result[0]
    #Paginator
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    url_paginator = "profile:paginator"

    return render_to_response("Cabinet/orderHistory.html", {"user": user, 'curr_url': curr_url,
                                                            'categotySelect': categotySelect, 'countryList': countryList,
                                                            'orderList': orderList, 'paginator_range': paginator_range,
                                                            'url_paginator': url_paginator, 'page': page})
@login_required(login_url=("/registration/"))
def get_favorite(request, page=1):
    #Categories list in header
    if request.POST:
        if len(request.POST) > 1:
            toDelete = request.POST.getlist("del[]")
            cabinet = Cabinet.objects.filter(user=request.user)
            favorites = Favorite.objects.filter(c2p__parent=cabinet, p2c__child__in=toDelete)
            favorites.delete()
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

    #Counrty list in header
    contrySorted = func.sortByAttr("Country", "NAME")
    sorted_id = [coun.id for coun in contrySorted]
    countryList = Item.getItemsAttributesValues(("NAME",), sorted_id)

    user = request.user
    curr_url = "favorite"
    cabinet = Cabinet.objects.filter(user=user)
    favorites = Favorite.active.get_active_related().filter(c2p__parent=cabinet).order_by('-create_date')
    products = Product.active.get_active_related().filter(c2p__parent__c2p__parent=cabinet, c2p__parent=favorites).order_by("-c2p__parent__create_date")

    attr = ("IMAGE", 'NAME', 'CURRENCY', 'COST', 'COUPON_DISCOUNT', 'DISCOUNT')

    result = func.setPaginationForItemsWithValues(products, *attr, page_num=5, page=page)
    favoriteList = result[0]
    for favorite in favoriteList.values():
        real_cost = _getRealCost(favorite)
        favorite.update({'AFTER_DISCOUNT': real_cost})

    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    url_paginator = "profile:favorite_paginator"



    return render_to_response('Cabinet/favorite.html', {'categotySelect': categotySelect, 'countryList':countryList,
                                                       'user': user, 'curr_url': curr_url, 'favoriteList': favoriteList,
                                                       'page': page, 'paginator_range': paginator_range,
                                                       'url_paginator': url_paginator},
                                                        context_instance=RequestContext(request))




def _getRealCost(productValues):
     if productValues.get('COUPON_DISCOUNT', False):
            totalCost = (float(productValues['COST'][0]) -
                   float(productValues['COST'][0])*(float(productValues['COUPON_DISCOUNT'][0])/100))
     elif productValues.get('DISCOUNT', False) and not productValues.get('COUPON_DISCOUNT', False):
            totalCost = (float(productValues['COST'][0]) -
                   float(productValues['COST'][0])*(float(productValues['DISCOUNT'][0])/100))
     else:
             totalCost = 0

     return  totalCost














