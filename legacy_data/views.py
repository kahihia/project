from django.http import HttpResponse, Http404
from legacy_data.models import *
from core.models import User, Relationship, Dictionary
from core.amazonMethods import add, addFile
from appl.models import Company, Tpp, Product, Country, Cabinet, Gallery, InnovationProject, AdditionalPages
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import Q
import datetime
import csv
from dateutil import parser
from tpp.SiteUrlMiddleWare import get_request
import base64
from django.utils.translation import trans_real
from django.utils.translation import get_language, ugettext_lazy as _

def users_reload_CSV_DB(request):
    '''
        Reload user's data from prepared CSV file named users_legacy.csv
        into buffer DB table LEGACY_DATA_L_USER
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load user data from CSV file into buffer table...')
    with open('c:\\data\\user_legacy.csv', 'r') as f:
    #with open('c:\\data\\test_users.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    for i in range(0, len(data), 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        username = bytearray(data[i][0]).decode(encoding='utf-8')
        if (bytearray(data[i][1]).decode(encoding='utf-8') == 'Y'):
            is_active = True
        else:
            is_active = False

        if not len(bytearray(data[i][2]).decode(encoding='utf-8')):
            update_date = None
        else:
            update_date = datetime.datetime.strptime(bytearray(data[i][2]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        first_name = bytearray(data[i][3]).decode(encoding='utf-8')

        if bytearray(data[i][4]).decode(encoding='utf-8') == '':
            buf = bytearray(data[i][3]).decode(encoding='utf-8').split(' ')
            last_name = buf[0]
            first_name = ''
            for index in range(1, len(buf), 1):
                if index == len(buf):
                    first_name += buf[index]
                else:
                    first_name += buf[index]+' '
        else:
            last_name = bytearray(data[i][4]).decode(encoding='utf-8')

        email = bytearray(data[i][5]).decode(encoding='utf-8')

        if not len(bytearray(data[i][6]).decode(encoding='utf-8')):
            last_visit_date = None
        else:
            last_visit_date = datetime.datetime.strptime(bytearray(data[i][6]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        btx_id = bytearray(data[i][7]).decode(encoding='utf-8')

        if not len(bytearray(data[i][8]).decode(encoding='utf-8')):
            reg_date = None
        else:
            reg_date = datetime.datetime.strptime(bytearray(data[i][8]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        profession = bytearray(data[i][9]).decode(encoding='utf-8')
        personal_www = bytearray(data[i][10]).decode(encoding='utf-8')
        icq = bytearray(data[i][11]).decode(encoding='utf-8')
        gender = bytearray(data[i][12]).decode(encoding='utf-8')
        birth_date = None #datetime.datetime.strptime(bytearray(data[i][13]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")
        photo = bytearray(data[i][14]).decode(encoding='utf-8')
        phone = bytearray(data[i][15]).decode(encoding='utf-8')
        fax = bytearray(data[i][16]).decode(encoding='utf-8')
        cellular = bytearray(data[i][17]).decode(encoding='utf-8')
        addr_street = bytearray(data[i][18]).decode(encoding='utf-8')
        addr_city = bytearray(data[i][19]).decode(encoding='utf-8')
        addr_state = bytearray(data[i][20]).decode(encoding='utf-8')
        addr_zip = bytearray(data[i][21]).decode(encoding='utf-8')
        addr_country = bytearray(data[i][22]).decode(encoding='utf-8')
        company = bytearray(data[i][23]).decode(encoding='utf-8')
        department = bytearray(data[i][24]).decode(encoding='utf-8')
        position = bytearray(data[i][25]).decode(encoding='utf-8')
        mid_name = bytearray(data[i][26]).decode(encoding='utf-8')
        skp = bytearray(data[i][27]).decode(encoding='utf-8')

        try:
            leg_usr, created = L_User.objects.get_or_create(username = username,\
                                    is_active = is_active,\
                                    first_name = first_name,\
                                    middle_name = mid_name,\
                                    last_name = last_name,\
                                    email = email,\
                                    btx_id = btx_id,\
                                    update_date = update_date,\
                                    last_visit_date = last_visit_date,\
                                    reg_date = reg_date,\
                                    profession = profession,\
                                    personal_www = personal_www,\
                                    icq = icq,\
                                    gender = gender,\
                                    birth_date = birth_date,\
                                    photo = photo,\
                                    phone = phone,\
                                    fax = fax,\
                                    cellular = cellular,\
                                    skype = skp,\
                                    addr_street = addr_street,\
                                    addr_city = addr_city,\
                                    addr_state = addr_state,\
                                    addr_zip = addr_zip,\
                                    addr_country = addr_country,\
                                    company = company,\
                                    department = department,\
                                    position = position)

            if not created:
                leg_usr.middle_name = mid_name
                leg_usr.skype = skp
                leg_usr.save()

        except:
            return HttpResponse('Migration process from CSV file into buffer DB was interrupted!\
                                Possible reason is duplicated data.')

        if not i%200:
            print('Milestone: ', i)

    print('Done. Quantity of processed strings:', i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Users were migrated from CSV into DB!')

def users_reload_DB_DB(request):
    '''
        Reload user's data from buffer DB table LEGACY_DATA_L_USER
        into TPP User objects (CORE_USER table)
    '''
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Reload users from buffer DB into TPP DB...')
    qty = L_User.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    user_lst = L_User.objects.filter(completed=False).all()
    i=1
    photo_root = 'C:'
    for usr in user_lst:
        request = get_request()
        # for data migration as batch process generate random IP address 0.rand().rand().rand() for avoiding bot checking
        request.META['REMOTE_ADDR'] = '0.'+str(randint(0, 255))+'.'+str(randint(0, 255))+'.'+str(randint(0, 255))
        try:
            new_user = User.objects.create_user(username=usr.username, email=usr.email, password=str(randint(1000000, 9999999)))
        except:
            #return HttpResponse('Migration process from buffer DB into TPP DB was interrupted!\
            #                    Possible reason is duplicated data.')
            print(usr.username, '##', usr.email, '##', ' Count: ', i)
            i += 1
            continue

        new_user.first_name = usr.first_name
        new_user.last_name = usr.last_name
        new_user.is_active = True
        '''
        if len(usr.photo):
            photo_path = add(photo_root + usr.photo)
        else:
            photo_path = ''
        new_user.avatar = photo_path
        '''
        new_user.save()

        #create Cabinet for user

        try:
            user_cab = Cabinet.objects.get_or_create(title='CABINET_USER_ID_' + str(new_user.pk), user = new_user, create_user = new_user)

        except:
            User.objects.filter(pk = new_user.pk).delete()
            continue

        address = usr.addr_zip + ',' + usr.addr_country + ',' + usr.addr_state + ',' + usr.addr_city + usr.addr_street
        address.strip()

        attr = {
                'ADDRESS': address,
                'BIRTHDAY': usr.birth_date,
                'ICQ': usr.icq,
                #'IMAGE': photo_path,
                'MOBILE_NUMBER': usr.cellular,
                'PERSONAL_FAX': usr.fax,
                'POSITION': usr.position,
                'PROFESSION': usr.profession,
                #'SEX': usr.gender,
                'SITE_NAME': usr.personal_www,
                'SKYPE': usr.skype,
                'TELEPHONE_NUMBER': usr.phone,
                'USER_FIRST_NAME': usr.first_name,
                'USER_MIDDLE_NAME': usr.middle_name,
                'USER_LAST_NAME': usr.last_name,
            }

        trans_real.activate('ru') #activate russian locale
        res = user_cab.setAttributeValue(attr, new_user)
        trans_real.deactivate() #deactivate russian locale
        if res:
            usr.tpp_id = new_user.pk
            usr.completed = True
            usr.save()

        #Add user to Company Creator Group
        g = Group.objects.get(name='Company Creator')
        g.user_set.add(new_user)

        if not i%200:
            print('Milestone: ', qty + i)
        i += 1

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)

    return HttpResponse('Users were migrated from buffer DB into TPP DB!')

def users_reload_email_sent(request):
    '''
        For users which were reloaded from prepared CSV file named users_legacy.csv
        send e-mail with url for password change notification.
    '''
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Sending notifications to users about password changing.')
    qty = L_User.objects.filter(completed=True, email_sent=True).count()
    print('Already was sent: ', qty)
    user_list = L_User.objects.filter(completed=True, email_sent=False).all()
    if len(user_list):
        for usr in user_list:
            form = PasswordResetForm({'email': usr.email})
            form.is_valid()
            form.save(from_email=settings.DEFAULT_FROM_EMAIL, email_template_name='legacy_data/password_reset_email.html')
            usr.email_sent=True
            usr.save()
    else:
        return HttpResponse('Nothing to send!')

    print('Done. Notifications to users were sent!')
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)

    return HttpResponse('Migrated users were notified by e-mail!')

def company_reload_CSV_DB(request):
    '''
        Reload companies' data from prepared CSV file named companies_legacy.csv
        into buffer DB table LEGACY_DATA_L_COMPANY
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load company data from CSV file into buffer table...')
    with open('c:\\data\\companies_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        short_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
        preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
        preview_text = bytearray(data[i][4]).decode(encoding='utf-8')
        detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
        detail_text = bytearray(data[i][6]).decode(encoding='utf-8')

        if not len(data[i][7]):
            create_date = None
        else:
            create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        tpp_name = bytearray(data[i][8]).decode(encoding='utf-8')
        moderator = bytearray(data[i][9]).decode(encoding='utf-8')
        if len(data[i][10]):
            full_name = bytearray(data[i][10]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", '').strip()
        else:
            full_name = short_name
        ur_address = bytearray(data[i][11]).decode(encoding='utf-8')
        fact_address = bytearray(data[i][12]).decode(encoding='utf-8')
        tel = bytearray(data[i][13]).decode(encoding='utf-8')
        fax = bytearray(data[i][14]).decode(encoding='utf-8')
        email = bytearray(data[i][15]).decode(encoding='utf-8')
        INN = bytearray(data[i][16]).decode(encoding='utf-8')
        KPP = bytearray(data[i][17]).decode(encoding='utf-8')
        OKVED = bytearray(data[i][27]).decode(encoding='utf-8')
        OKATO = bytearray(data[i][28]).decode(encoding='utf-8')
        OKPO = bytearray(data[i][29]).decode(encoding='utf-8')
        bank_account = bytearray(data[i][18]).decode(encoding='utf-8')
        bank_name = bytearray(data[i][19]).decode(encoding='utf-8')
        director_name = bytearray(data[i][20]).decode(encoding='utf-8')
        bux_name = bytearray(data[i][21]).decode(encoding='utf-8')
        slogan = bytearray(data[i][22]).decode(encoding='utf-8')

        if (data[i][23] == 'Y'):
            is_active = True
        else:
            is_active = False

        branch = bytearray(data[i][24]).decode(encoding='utf-8')
        experts = bytearray(data[i][25]).decode(encoding='utf-8')
        map_id = bytearray(data[i][26]).decode(encoding='utf-8')
        site = bytearray(data[i][30]).decode(encoding='utf-8')
        country_name = bytearray(data[i][31]).decode(encoding='utf-8')

        if (data[i][32] == 'Y'):
            is_deleted = True
        else:
            is_deleted = False

        keywords = bytearray(data[i][33]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                            replace("&amp;", '').strip()

        try:
            L_Company.objects.create(
                                            btx_id = btx_id,\
                                            short_name = short_name,\
                                            detail_page_url = detail_page_url,\
                                            preview_picture = preview_picture,\
                                            preview_text = preview_text,\
                                            detail_picture = detail_picture,\
                                            detail_text = detail_text,\
                                            create_date = create_date,\
                                            tpp_name = tpp_name,\
                                            moderator = moderator,\
                                            full_name = full_name,\
                                            ur_address = ur_address,\
                                            fact_address = fact_address,\
                                            tel = tel,\
                                            fax = fax,\
                                            email = email,\
                                            INN = INN,\
                                            KPP = KPP,\
                                            OKVED = OKVED,\
                                            OKATO = OKATO,\
                                            OKPO = OKPO,\
                                            bank_account = bank_account,\
                                            bank_name = bank_name,\
                                            director_name = director_name,\
                                            bux_name = bux_name,\
                                            slogan = slogan,\
                                            is_active = is_active,\
                                            branch = branch,\
                                            experts = experts,\
                                            map_id = map_id,\
                                            site = site,\
                                            country_name = country_name,\
                                            is_deleted = is_deleted,\
                                            keywords = keywords)
            count += 1
        except:
            #print('Milestone: ', i+1)
            print(btx_id, '##', short_name, '##', ' Count: ', i+1)
            continue

        #print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Companies were migrated from CSV into DB!')

def company_reload_DB_DB(request):
    '''
        Reload companies' data from buffer DB table LEGACY_DATA_L_COMPANY into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move users from buffer table into original tables
    print('Data validation. Please, wait...')
    qty = L_Company.objects.filter(country_name='').count()
    if qty:
        L_Company.objects.filter(country_name='').delete()
        print('Were deleted companies without countries: ', qty)
    print('Reload companies from buffer DB into TPP DB...')
    qty = L_Company.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    flag = True
    block_size = 1000
    i = 0
    while flag:
        comp_lst = L_Company.objects.filter(completed=False).all()[:block_size]
        if len(comp_lst) < block_size: # it will last big loop
            flag = False
        #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
        #comp_lst = L_Company.objects.filter(pk=545208)

        for leg_cmp in comp_lst:
            #set create_user (owner) for the Company
            if leg_cmp.moderator:
                try:
                    l_user = L_User.objects.get(btx_id=leg_cmp.moderator)
                    create_usr = User.objects.get(pk=l_user.tpp_id)
                except:
                    create_usr = User.objects.get(pk=1)
            else:
                create_usr = User.objects.get(pk=1)

            try:
                new_comp = Company.objects.create(title='COMPANY_LEG_ID:'+leg_cmp.btx_id,
                                                  create_user=create_usr)
            except:
                print(leg_cmp.btx_id, '##', leg_cmp.short_name, '##', ' Count: ', i)
                i += 1
                continue
            '''
            if len(leg_cmp.preview_picture):
                img_small_path = add(img_root + leg_cmp.preview_picture)
            else:
                img_small_path = ''
            if len(leg_cmp.detail_picture):
                img_detail_path = add(img_root + leg_cmp.detail_picture)
            else:
                img_detail_path = ''
            '''
            img_small_path = ''
            img_detail_path = ''
            #if wrong VATIN then generate default
            if len(leg_cmp.INN) < 5:
                inn = 'INN_' + str(randint(1000000000, 9999999999))
            else:
                inn = leg_cmp.INN

            attr = {'NAME': leg_cmp.short_name,
                    'IMAGE_SMALL': img_small_path,
                    'ANONS': leg_cmp.preview_text,
                    'IMAGE': img_detail_path,
                    'DETAIL_TEXT': leg_cmp.detail_text,
                    'NAME_FULL': leg_cmp.full_name,
                    'ADDRESS_YURID': leg_cmp.ur_address,
                    'ADDRESS_FACT': leg_cmp.fact_address,
                    'ADDRESS': leg_cmp.fact_address,
                    'TELEPHONE_NUMBER': leg_cmp.tel,
                    'FAX': leg_cmp.fax,
                    'EMAIL': leg_cmp.email,
                    'INN': inn,
                    'KPP': leg_cmp.KPP,
                    'OKVED': leg_cmp.OKVED,
                    'OKATO': leg_cmp.OKATO,
                    'OKPO': leg_cmp.OKPO,
                    'BANK_ACCOUNT': leg_cmp.bank_account,
                    'BANK_NAME': leg_cmp.bank_name,
                    'NAME_DIRECTOR': leg_cmp.director_name,
                    'NAME_BUX': leg_cmp.bux_name,
                    'SLOGAN': leg_cmp.slogan,
                    'MAP_POSITION': leg_cmp.map_id,
                }

            trans_real.activate('ru') #activate russian locale
            res = new_comp.setAttributeValue(attr, create_usr)
            trans_real.deactivate() #deactivate russian locale
            if res:
                leg_cmp.tpp_id = new_comp.pk
                leg_cmp.completed = True
                leg_cmp.save()
                if not leg_cmp.tpp_name:
                    new_comp.end_date = datetime.datetime.now()
                    new_comp.save()
            else:
                print('Problems with Attributes adding!')
                i += 1
                continue

            # add workers to Company's community
            lst_wrk = L_User.objects.filter(company=leg_cmp.short_name)
            for wrk in lst_wrk:
                g = Group.objects.get(name=new_comp.community)
                try:
                    wrk_obj = User.objects.get(pk=wrk.tpp_id)
                    g.user_set.add(wrk_obj)
                except:
                    continue

            # create relationship type=Dependence with country
            try: #if there isn't country in Company take it from TPP
                prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=leg_cmp.country_name)
            except:
                tpp = L_TPP.objects.filter(btx_id=leg_cmp.tpp_name)
                try:
                    prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=tpp[0].country)
                except:
                    L_Company.objects.filter(btx_id=leg_cmp.btx_id).delete()
                    Company.objects.filter(pk=leg_cmp.tpp_id).delete()
                    i += 1
                    continue

            Relationship.objects.create(parent=prnt, type='dependence', child=new_comp, create_user=create_usr)

            i += 1
            print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Companies were migrated from buffer DB into TPP DB!')


def product_reload_CSV_DB(request):
    '''
        Reload products' data from prepared CSV file named product_legacy.csv
        into buffer DB table LEGACY_DATA_L_PRODUCT
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load product data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\product_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        prod_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
        preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
        preview_text = bytearray(data[i][4]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                            replace("&amp;", '').strip()
        detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
        detail_text = bytearray(data[i][6]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                            replace("&amp;", '').strip()

        if not len(data[i][7]):
            create_date = None
        else:
            create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        company_id = bytearray(data[i][8]).decode(encoding='utf-8')
        photos1 = bytearray(data[i][9]).decode(encoding='utf-8')
        discount = bytearray(data[i][10]).decode(encoding='utf-8')
        add_pages = bytearray(data[i][11]).decode(encoding='utf-8')
        tpp = bytearray(data[i][12]).decode(encoding='utf-8')
        direction = bytearray(data[i][13]).decode(encoding='utf-8')
        if (data[i][14] == 'Y'):
            is_deleted = True
        else:
            is_deleted = False
        photos2 = bytearray(data[i][15]).decode(encoding='utf-8')
        file = bytearray(data[i][16]).decode(encoding='utf-8')
        keywords = bytearray(data[i][17]).decode(encoding='utf-8').replace("&quot;", '"').replace("quot;", '"').\
                                            replace("&amp;", '').strip()

        try:
            L_Product.objects.create(
                                            btx_id = btx_id,\
                                            prod_name = prod_name,\
                                            detail_page_url = detail_page_url,\
                                            preview_picture = preview_picture,\
                                            preview_text = preview_text,\
                                            detail_picture = detail_picture,\
                                            detail_text = detail_text,\
                                            create_date = create_date,\
                                            company_id = company_id,\
                                            photos1 = photos1,\
                                            discount = discount,\
                                            add_pages = add_pages,\
                                            tpp = tpp,\
                                            direction = direction,\
                                            is_deleted = is_deleted,\
                                            photos2 = photos2,\
                                            file = file,\
                                            keywords = keywords)
            count += 1
        except:
            #print('Milestone: ', i+1)
            print(btx_id, '##', prod_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Products were migrated from CSV into DB!')

def product_reload_DB_DB(request):
    '''
        Reload products' data from buffer DB table LEGACY_DATA_L_PRODUCT into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move products from buffer table into original tables
    print('Reload products from buffer DB into TPP DB...')
    qty = L_Product.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    prod_lst = L_Product.objects.filter(completed=False).all()
    #comp_lst = L_Company.objects.exclude(preview_picture='')[:2]
    #comp_lst = L_Company.objects.filter(pk=545208)
    i = 0
    count = 0;
    create_usr = User.objects.get(pk=1)
    for leg_prod in prod_lst:
        try:
            new_prod = Product.objects.create(title='PRODUCT_LEG_ID:'+leg_prod.btx_id,
                                              create_user=create_usr)
            count += 1
        except:
            print(leg_prod.btx_id, '##', leg_prod.prod_name, '##', ' Count: ', i)
            i += 1
            continue
        '''
        if len(leg_prod.preview_picture):
            img_small_path = add(img_root + leg_prod.preview_picture)
        else:
            img_small_path = ''
        if len(leg_prod.detail_picture):
            img_detail_path = add(img_root + leg_prod.detail_picture)
        else:
            img_detail_path = ''
        '''
        img_small_path = ''
        img_detail_path = ''
        attr = {
                'NAME': leg_prod.prod_name,
                'IMAGE_SMALL': img_small_path,
                'ANONS': leg_prod.preview_text,
                'IMAGE': img_detail_path,
                'DETAIL_TEXT': leg_prod.detail_text,
                'DISCOUNT': leg_prod.discount,
            }
        trans_real.activate('ru')
        res = new_prod.setAttributeValue(attr, create_usr)
        trans_real.deactivate()
        if res:
            leg_prod.tpp_id = new_prod.pk
            leg_prod.completed = True
            leg_prod.save()
        else:
            print('Problems with Attributes adding!')
            i += 1
            continue

        # create relationship type=Dependence with Company
        try:
            cmp = L_Company.objects.get(btx_id=leg_prod.company_id)
            prnt = Company.objects.get(pk=cmp.tpp_id)
            Relationship.objects.create(parent=prnt, type='dependence', child=new_prod, create_user=create_usr)
        except:
            print('Product was deleted! Product btx_id:', leg_prod.btx_id)
            Product.objects.filter(pk=new_prod.pk).delete()
            count -= 1
            print('Milestone: ', qty + i)
            i += 1
            continue

        print('Relationship between Product and Company was created! Prod_id:', new_prod.pk)

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Products were migrated from buffer DB into TPP DB!')

def tpp_reload_CSV_DB(request):
    '''
        Reload TPPs' data from prepared CSV file named product_legacy.csv
        into buffer DB table LEGACY_DATA_L_TPP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load product data from CSV file into buffer table...')
    with open('c:\\data\\tpp_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        tpp_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
        preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
        preview_text = bytearray(data[i][4]).decode(encoding='utf-8')
        detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
        detail_text = bytearray(data[i][6]).decode(encoding='utf-8')

        if not len(data[i][7]):
            create_date = None
        else:
            create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        country = bytearray(data[i][8]).decode(encoding='utf-8')
        moderator = bytearray(data[i][9]).decode(encoding='utf-8')
        head_pic = bytearray(data[i][10]).decode(encoding='utf-8')
        logo = bytearray(data[i][11]).decode(encoding='utf-8')
        domain = bytearray(data[i][12]).decode(encoding='utf-8')
        header_letter = bytearray(data[i][13]).decode(encoding='utf-8')
        member_letter = bytearray(data[i][14]).decode(encoding='utf-8')
        address = bytearray(data[i][15]).decode(encoding='utf-8')
        email = bytearray(data[i][16]).decode(encoding='utf-8')
        fax = bytearray(data[i][17]).decode(encoding='utf-8')
        map = bytearray(data[i][18]).decode(encoding='utf-8')
        tpp_parent = bytearray(data[i][19]).decode(encoding='utf-8')
        phone = bytearray(data[i][20]).decode(encoding='utf-8')
        extra = bytearray(data[i][21]).decode(encoding='utf-8')

        try:
            L_TPP.objects.create(btx_id = btx_id,\
                                tpp_name = tpp_name,\
                                detail_page_url = detail_page_url,\
                                preview_picture = preview_picture,\
                                preview_text = preview_text,\
                                detail_picture = detail_picture,\
                                detail_text = detail_text,\
                                create_date = create_date,\
                                country = country,\
                                moderator = moderator,\
                                head_pic = head_pic,\
                                logo = logo,\
                                domain = domain,\
                                header_letter = header_letter,\
                                member_letter = member_letter,\
                                address = address,\
                                email = email,\
                                fax = fax,\
                                map = map,\
                                tpp_parent = tpp_parent,\
                                phone = phone,\
                                extra = extra)
            count += 1
        except:
            print('Milestone: ', i+1)
            print(btx_id, '##', tpp_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPPs were migrated from CSV into DB!')

def tpp_reload_DB_DB(request):
    '''
        Reload TPPs' data from buffer DB table LEGACY_DATA_L_TPP into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    print('Loading TPPs from buffer DB into TPP DB...')
    qty = L_TPP.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    i = 0
    tpp_lst = L_TPP.objects.filter(completed=False).all()
    for leg_tpp in tpp_lst:
        #set create_user (owner) for the TPP
        if leg_tpp.moderator:
            try:
                l_user = L_User.objects.get(btx_id=leg_tpp.moderator)
                create_usr = User.objects.get(pk=l_user.tpp_id)
            except:
                create_usr = User.objects.get(pk=1)
        else:
            create_usr = User.objects.get(pk=1)

        try:
            new_tpp = Tpp.objects.create(title='TPP_LEG_ID:'+leg_tpp.btx_id,
                                                  create_user=create_usr)
        except:
            print(leg_tpp.btx_id, '##', leg_tpp.tpp_name, '##', ' Count: ', i)
            i += 1
            continue

        '''
        if len(leg_tpp.preview_picture):
            img_small_path = add(img_root + leg_tpp.preview_picture)
        else:
            img_small_path = ''
        if len(leg_tpp.detail_picture):
            img_detail_path = add(img_root + leg_tpp.detail_picture)
        else:
            img_detail_path = ''
        if len(leg_tpp.head_pic):
            head_pic_path = add(img_root + leg_tpp.head_pic)
        else:
            head_pic_path = ''

        '''
        img_small_path = ''
        img_detail_path = ''
        head_pic_path = ''

        attr = {'NAME': leg_tpp.tpp_name,
                'IMAGE_SMALL': img_small_path,
                'ANONS': leg_tpp.preview_text,
                'IMAGE': img_detail_path,
                'DETAIL_TEXT': leg_tpp.detail_text,
                'HEAD_PIC': head_pic_path,
                'SITE_NAME': leg_tpp.domain,
                'ADDRESS': leg_tpp.address,
                'EMAIL': leg_tpp.email,
                'FAX': leg_tpp.fax,
                'MAP_POSITION': leg_tpp.map,
                'TELEPHONE_NUMBER': leg_tpp.phone,
            }

        trans_real.activate('ru') #activate russian locale
        res = new_tpp.setAttributeValue(attr, create_usr)
        trans_real.deactivate() #deactivate russian locale
        if res:
            leg_tpp.tpp_id = new_tpp.pk
            leg_tpp.completed = True
            leg_tpp.save()
        else:
            print('Problems with Attributes adding!')
            i += 1
            continue

        # create relationship type=Dependence with country
        try: #if there isn't country in Company take it from TPP
            prnt = Country.objects.get(item2value__attr__title="NAME", item2value__title_ru=leg_tpp.country)

            Relationship.objects.create(parent=prnt, type='dependence', child=new_tpp, create_user=create_usr)
        except:
            trans_real.activate('ru')
            print('Next TPP has not country:', new_tpp.getName())
            trans_real.deactivate()

        i += 1
        print('Milestone: ', qty + i)

    #set up mother TPP
    tpp_lst = L_TPP.objects.exclude(tpp_parent='').all()
    for tpp in tpp_lst:
        try:
            parent_tpp = Tpp.objects.get(pk=L_TPP.objects.get(btx_id=tpp.tpp_parent).tpp_id)
            child_tpp = Tpp.objects.get(pk=tpp.tpp_id)
            Relationship.objects.create(parent=parent_tpp, type='hierarchy', child=child_tpp, create_user=create_usr)
            print('Relationship for parent TPPs was created!')
        except:
            continue

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPPs were migrated from buffer DB into TPP DB!')

def pic2prod_CSV_DB(request):
    '''
        Reload products' pictures from prepared CSV file named pic2prod_legacy.csv
        into buffer DB table LEGACY_DATA_L_PIC2PROD
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\pic2prod_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        prod_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        preview_picture = bytearray(data[i][2]).decode(encoding='utf-8')
        detail_picture = bytearray(data[i][3]).decode(encoding='utf-8')
        gallery = bytearray(data[i][4]).decode(encoding='utf-8')

        try:
            L_Pic2Prod.objects.create(  btx_id = btx_id,\
                                        prod_name = prod_name,\
                                        preview_picture = preview_picture,\
                                        detail_picture = detail_picture,\
                                        gallery = gallery)
            count += 1
        except Exception as e:
            #print('Milestone: ', i+1)
            i += 1
            print(btx_id, '##', prod_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Pictures for Products were migrated from CSV into DB!')

def pic2prod_DB_DB(request):
    '''
        Reload products' pictures from buffer DB table LEGACY_DATA_L_PIC2PROD into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move products' pictures from buffer table into original tables
    print('Reload products from buffer DB into TPP DB...')
    qty = L_Pic2Prod.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    pic_lst = L_Pic2Prod.objects.filter(completed=False).all()
    #pic_lst = L_Pic2Prod.objects.filter(completed=False)[:10]
    i = 0
    count = 0;
    prev_btx_id = 0;
    create_usr = User.objects.get(pk=1)
    for rec in pic_lst:
        if prev_btx_id != rec.btx_id:
            try:
                leg_prod = L_Product.objects.get(btx_id=rec.btx_id)
            except:
                i += 1
                continue
            try:
                prod = Product.objects.get(pk=leg_prod.tpp_id)
            except:
                i += 1
                continue

            prev_btx_id = rec.btx_id

            if len(rec.preview_picture):
                img_small_path = add(img_root + rec.preview_picture)
            else:
                img_small_path = ''
            if len(rec.detail_picture):
                img_detail_path = add(img_root + rec.detail_picture)
            else:
                img_detail_path = ''

            attr = {
                    'IMAGE_SMALL': img_small_path,
                    'IMAGE': img_detail_path,
                }
            trans_real.activate('ru')
            res = prod.setAttributeValue(attr, create_usr)
            trans_real.deactivate()
            if not res:
                print('Problems with Attributes adding!')
                i += 1
                continue

        rec.tpp_id = prod.pk
        rec.completed = True
        rec.save()

        if len(rec.gallery): #create relationship with Gallery
            try:
                gal = Gallery.objects.create(title='GALLERY_FOR_PROD_ID:'+rec.btx_id, create_user=create_usr)
            except:
                i += 1
                continue

            gal.photo = add(img_root + rec.gallery)
            # create relationship
            try:
                Relationship.objects.create(parent=prod, type='relation', child=gal, create_user=create_usr)
                print('Relationship between Product and Gallery was created! Prod_id:', prod.pk)
                count += 1
            except:
                print('Product was deleted! Product btx_id:', leg_prod.btx_id)
                gal.delete()
                count -= 1
                i += 1
                continue

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Product pictures were migrated from buffer DB into TPP DB!')

def pic2org_CSV_DB(request):
    '''
        Reload companies' pictures from prepared CSV file named pic2comp_legacy.csv
        into buffer DB table LEGACY_DATA_L_PIC2ORG
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Load data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\pic2org_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        gallery_topic = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        gallery = bytearray(data[i][2]).decode(encoding='utf-8')
        pic_title = bytearray(data[i][3]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()

        try:
            L_Pic2Org.objects.create(   btx_id=btx_id,\
                                        gallery_topic=gallery_topic,\
                                        gallery=gallery,\
                                        pic_title=pic_title)
            count += 1
        except:
            #print('Milestone: ', i+1)
            i += 1
            print(btx_id, '##', gallery_topic, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Pictures for Products were migrated from CSV into DB!')

def pic2org_DB_DB(request):
    '''
        Reload products' pictures from buffer DB table LEGACY_DATA_L_PIC2ORG into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    # Move products' pictures from buffer table into original tables
    print('Reload products from buffer DB into TPP DB...')
    qty = L_Pic2Org.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    pic_lst = L_Pic2Org.objects.filter(completed=False).all()
    #pic_lst = L_Pic2Org.objects.filter(completed=False)[:1000]
    i = 0
    count = 0;
    prev_btx_id = 0;
    create_usr = User.objects.get(pk=1)
    for rec in pic_lst:
        if prev_btx_id != rec.btx_id:
            try:
                leg_org = L_Company.objects.get(btx_id=rec.btx_id)
            except:
                try:
                    leg_org = L_TPP.objects.get(btx_id=rec.btx_id)
                except:
                    print('ATTENTION! Legacy Organization not found! Org ID:', rec.btx_id)
                    rec.completed = True
                    rec.save()
                    i += 1
                    continue
            try:
                org = Company.objects.get(pk=leg_org.tpp_id)
            except:
                try:
                    org = Tpp.objects.get(pk=leg_org.tpp_id)
                except:
                    print('ATTENTION! Organization not found! Org ID:', leg_org.tpp_id)
                    i += 1
                    continue

            prev_btx_id = rec.btx_id

            if len(leg_org.preview_picture):
                img_small_path = add(img_root + leg_org.preview_picture)
            else:
                img_small_path = ''
            if len(leg_org.detail_picture):
                img_detail_path = add(img_root + leg_org.detail_picture)
            else:
                img_detail_path = ''

            attr = {
                    'IMAGE_SMALL': img_small_path,
                    'IMAGE': img_detail_path,
                }
            trans_real.activate('ru')
            res = org.setAttributeValue(attr, create_usr)
            trans_real.deactivate()
            if not res:
                print('Problems with Attributes adding!')
                i += 1
                continue

        if len(rec.gallery): #create relationship with Gallery
            try:
                gal = Gallery.objects.create(title='GALLERY_FOR_ORG_ID:'+rec.btx_id,\
                                             photo = add(img_root + rec.gallery), create_user=create_usr)
                attr = {
                    'GALLERY_TOPIC': rec.gallery_topic,
                    'NAME': rec.pic_title,
                }
                trans_real.activate('ru')
                res = org.setAttributeValue(attr, create_usr)
                trans_real.deactivate()
                if not res:
                    print('Problems with Attributes adding!')
                    i += 1
                    continue
            except:
                print('Can not create Gallery! Organization ID: ', org.pk)
                i += 1
                continue
            
            # create relationship
            try:
                Relationship.objects.create(parent=org, type='relation', child=gal, create_user=create_usr)
                rec.tpp_id = org.pk
                rec.save()
                leg_org.pic_completed = True
                leg_org.save()
                print('Relationship between Organization and Gallery was created! Org_id:', org.pk)
                count += 1
            except:
                print('Can not establish gallery relationship! Organization btx_id:', leg_org.btx_id)
                gal.delete()
                count -= 1
                i += 1
                continue

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Organization pictures were migrated from buffer DB into TPP DB!')

def comp2tpp_DB_DB(request):
    '''
        Create relationships between companies and their TPP
    '''
    print('Create relationships between Companies and their TPP...')
    time1 = datetime.datetime.now()
    comp_lst = L_Company.objects.exclude(tpp_name='').all()
    #comp_lst = L_Company.objects.exclude(tpp_name='')[:10]
    i = 0
    count = 0;
    create_usr = User.objects.get(pk=1)
    flag = True
    start = 0
    block_size = 1000
    i = 0
    while flag:
        comp_lst = L_Company.objects.exclude(tpp_name='').all()[start:start+block_size]
        if len(comp_lst) < block_size: # it will last big loop
            flag = False
        else:
            start += block_size

        for cmp in comp_lst:
            try:
                company = Company.objects.get(pk=cmp.tpp_id)
            except:
                print('Company does not exist in DB! Company btx_id:', cmp.btx_id)
                i += 1
                continue

            try:
                leg_tpp = L_TPP.objects.get(btx_id=cmp.tpp_name)
            except:
                print('Legacy TPP does not exist in DB! TPP btx_id:', cmp.tpp_name)
                i += 1
                continue

            try:
                tpp = Tpp.objects.get(pk=leg_tpp.tpp_id)
            except:
                print('TPP does not exist in DB! TPP btx_id:', cmp.tpp_name)
                i += 1
                continue

            # create relationship
            try:
                Relationship.objects.create(parent=tpp, type='relation', child=company, create_user=create_usr)
                count += 1
            except:
                print('Can not establish relationship! Company ID:', company.pk, ' TPP ID:', tpp.pk)
                i += 1
                continue

            i += 1
            print('Milestone: ', i)

    print('Done. Quantity of processed strings:', i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Relationships between Companies and their TPP were created!')

def site2prod_CSV_DB(request):
    '''
        Reload products' sections from prepared CSV file named site2prod_legacy.csv
        into buffer DB table LEGACY_DATA_L_SITE2PROD
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\site2prod_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        section_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        product_name = bytearray(data[i][2]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()

        try:
            L_Site2Prod.objects.create( btx_id=btx_id,\
                                        section_name=section_name,\
                                        product_name=product_name)
            count += 1
        except:
            #print('Milestone: ', i+1)
            i += 1
            print(btx_id, '##', product_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Sites for Products were migrated from CSV into DB!')

def site2prod_DB_DB(request):
    '''
        Update site attribute for products
    '''
    print('Updating B2C products...')
    time1 = datetime.datetime.now()
    qty = L_Site2Prod.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    prod_lst = L_Site2Prod.objects.filter(completed=False).all()

    b2c_site = 0
    b2b_site = 0

    i = 0
    count = 0

    for itm in prod_lst:
        try:
            leg_prod = L_Product.objects.get(btx_id=itm.btx_id)
        except:
            print('Product does not exist in buffer DB! Product btx_id:', itm.btx_id)
            i += 1
            continue

        try:
            prod = Product.objects.get(pk=leg_prod.tpp_id)
        except:
            print('Product does not exist in TPP DB! Product btx_id:', itm.btx_id)
            i += 1
            continue

        prod.sites.add(b2c_site)
        itm.completed = True
        itm.save()
        count += 1
        i += 1
        print('Milestone: ', i)

    print('Updating B2B products...')
    start = 0
    block_size = 1000
    flag = True
    j = 0
    while flag:
        prod_lst = Product.objects.exclude(sites=b2c_site).all()[start:start+block_size]
        if len(prod_lst) < block_size:
            flag = False
        else:
            start += block_size

        for prod in prod_lst:
            prod.sites.add(b2b_site)
            j += 1
            count += 1
            print('Milestone: ', j)

    print('Done. Quantity of processed items:', i+j, 'Were updated:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Production sites were updated!')

def moder2comp_CSV_DB(request):
    '''
        Reload company moderators from prepared CSV file named comp_moder_legacy.csv
        into buffer DB table LEGACY_DATA_L_MODER2COMP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\comp_moder_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        org_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        moder_btx_id = bytearray(data[i][2]).decode(encoding='utf-8')

        try:
            L_Moder2Comp.objects.create( btx_id=btx_id,\
                                        org_name=org_name,\
                                        moder_btx_id=moder_btx_id)
            count += 1
        except:
            #print('Milestone: ', i+1)
            i += 1
            print(btx_id, '##', org_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Company moderators were migrated from CSV into buffer DB!')

def moder2comp_DB_DB(request):
    '''
        Create relationships between companies and their moderators
    '''
    #for debugging - clear all ORG-XXXXXX groups from users
    time1 = datetime.datetime.now()
    '''
    i = 0
    print('Removing users from ORG-xxxxxxx groups. Please, wait...')
    g_lst = Group.objects.filter(name__icontains='ORG-').all()
    for g in g_lst:
        usr_list = g.user_set.all()
        for usr in usr_list:
            g.user_set.remove(usr)
            i += 1
            if not i%200:
                print('Removing Milestone:', i)
    '''
    print('Create relationships between Companies and their moderators.')
    print('Verifying data. Please, wait...')
    qty = L_Moder2Comp.objects.filter(~Q(moder_btx_id='')).count()
    try:
        L_Moder2Comp.objects.filter(moder_btx_id='').delete()
        print('Were deleted', qty, 'items without moderator IDs.')
    except:
        pass

    qty = L_Moder2Comp.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)

    count = 0
    flag = True
    block_size = 1000
    i = 0

    while flag:
        moder_lst = L_Moder2Comp.objects.filter(completed=False)[:block_size]
        if len(moder_lst) < block_size: # it will last big loop
            flag = False

        for moder in moder_lst:
            moder.completed = True
            moder.save()
            try:
                leg_comp = L_Company.objects.get(btx_id=moder.btx_id)
            except:
                print('Company does not exist in buffer DB! Company btx_id:', moder.btx_id)
                i += 1
                continue

            try:
                comp = Company.objects.get(pk=leg_comp.tpp_id)
            except:
                print('Company does not exist in TPP DB! Company ID:', leg_comp.tpp_id)
                i += 1
                continue

            try:
                leg_user = L_User.objects.get(btx_id=moder.moder_btx_id)
            except:
                print('Legacy User does not exist in buffer DB! User btx_id:', moder.moder_btx_id)
                i += 1
                continue

            try:
                moder_user = User.objects.get(pk=leg_user.tpp_id)
            except:
                print('User does not exist in TPP DB! User ID:', leg_user.tpp_id)
                i += 1
                continue

            # add moderator to company's community
            try:
                g = Group.objects.get(name=comp.community)
                g.user_set.add(moder_user)
            except:
                print('Can not access to community! Company community:', comp.community)
                i += 1
                continue

            moder_user.is_manager = True
            moder_user.save()
            count += 1

            i += 1
            print('Milestone: ', i)

    print('Done. Quantity of processed strings:', i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Relationships between Companies and their moderators were created!')

def moder2tpp_CSV_DB(request):
    '''
        Reload company moderators from prepared CSV file named tpp_moder_legacy.csv
        into buffer DB table LEGACY_DATA_L_MODER2TPP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading data from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\tpp_moder_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        org_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        moder_btx_id = bytearray(data[i][2]).decode(encoding='utf-8')

        try:
            L_Moder2Tpp.objects.create( btx_id=btx_id,\
                                        org_name=org_name,\
                                        moder_btx_id=moder_btx_id)
            count += 1
        except:
            #print('Milestone: ', i+1)
            i += 1
            print(btx_id, '##', org_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPP moderators were migrated from CSV into buffer DB!')

def moder2tpp_DB_DB(request):
    '''
        Create relationships between TPPs and their moderators
    '''
    #for debugging - clear all ORG-XXXXXX groups from users
    time1 = datetime.datetime.now()
    '''
    i = 0
    print('Removing users from ORG-xxxxxxx groups. Please, wait...')
    g_lst = Group.objects.filter(name__icontains='ORG-').all()
    for g in g_lst:
        usr_list = g.user_set.all()
        for usr in usr_list:
            g.user_set.remove(usr)
            i += 1
            if not i%200:
                print('Removing Milestone:', i)
    '''
    print('Create relationships between TPPs and their moderators.')
    print('Verifying data. Please, wait...')
    qty = L_Moder2Tpp.objects.filter(~Q(moder_btx_id='')).count()
    try:
        L_Moder2Tpp.objects.filter(moder_btx_id='').delete()
        print('Were deleted', qty, 'items without moderator IDs.')
    except:
        pass

    qty = L_Moder2Tpp.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)

    count = 0
    flag = True
    block_size = 1000
    i = 0

    while flag:
        moder_lst = L_Moder2Tpp.objects.filter(completed=False)[:block_size]
        if len(moder_lst) < block_size: # it will last big loop
            flag = False

        for moder in moder_lst:
            moder.completed = True
            moder.save()
            try:
                leg_tpp = L_TPP.objects.get(btx_id=moder.btx_id)
            except:
                print('TPP does not exist in buffer DB! TPP btx_id:', moder.btx_id)
                i += 1
                continue

            try:
                tpp = Tpp.objects.get(pk=leg_tpp.tpp_id)
            except:
                print('TPP does not exist in TPP DB! TPP ID:', leg_tpp.tpp_id)
                i += 1
                continue

            try:
                leg_user = L_User.objects.get(btx_id=moder.moder_btx_id)
            except:
                print('Legacy User does not exist in buffer DB! User btx_id:', moder.moder_btx_id)
                i += 1
                continue

            try:
                moder_user = User.objects.get(pk=leg_user.tpp_id)
            except:
                print('User does not exist in TPP DB! User ID:', leg_user.tpp_id)
                i += 1
                continue

            # add moderator to TPP's community
            try:
                g = Group.objects.get(name=tpp.community)
                g.user_set.add(moder_user)
            except:
                print('Can not access to community! TPP community:', tpp.community)
                i += 1
                continue

            moder_user.is_manager = True
            moder_user.save()
            count += 1

            i += 1
            print('Milestone: ', i)

    print('Done. Quantity of processed strings:', i, 'Were added into DB:', count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Relationships between TPPs and their moderators were created!')

def innprj_CSV_DB(request):
    '''
        Reload Innovative Projects data from prepared CSV file named innov_prj_legacy.csv
        into buffer DB table LEGACY_DATA_L_INNPRJ
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading Innovative Projects from CSV file into buffer table...')
    with open('c:\\data\\innov_prj_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        prj_name = bytearray(data[i][1]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()
        detail_page_url = bytearray(data[i][2]).decode(encoding='utf-8')
        preview_picture = bytearray(data[i][3]).decode(encoding='utf-8')
        preview_text = bytearray(data[i][4]).decode(encoding='utf-8')
        detail_picture = bytearray(data[i][5]).decode(encoding='utf-8')
        detail_text = bytearray(data[i][6]).decode(encoding='utf-8')

        if not len(data[i][7]):
            create_date = None
        else:
            create_date = datetime.datetime.strptime(bytearray(data[i][7]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")

        author = bytearray(data[i][8]).decode(encoding='utf-8')
        industry = bytearray(data[i][9]).decode(encoding='utf-8')
        company = bytearray(data[i][10]).decode(encoding='utf-8')
        tpp = bytearray(data[i][11]).decode(encoding='utf-8')
        prj_title = bytearray(data[i][12]).decode(encoding='utf-8')
        fax = bytearray(data[i][13]).decode(encoding='utf-8')
        phone = bytearray(data[i][14]).decode(encoding='utf-8')
        email = bytearray(data[i][15]).decode(encoding='utf-8')
        tech_info = bytearray(data[i][16]).decode(encoding='utf-8')
        deleted = bytearray(data[i][17]).decode(encoding='utf-8')
        keywords = bytearray(data[i][18]).decode(encoding='utf-8')
        private_name = bytearray(data[i][19]).decode(encoding='utf-8')
        private_resume = bytearray(data[i][20]).decode(encoding='utf-8')
        country = bytearray(data[i][21]).decode(encoding='utf-8')
        site = bytearray(data[i][22]).decode(encoding='utf-8')
        project_name = bytearray(data[i][23]).decode(encoding='utf-8')
        project_point = bytearray(data[i][24]).decode(encoding='utf-8')
        target_community = bytearray(data[i][25]).decode(encoding='utf-8')
        prj_sum = bytearray(data[i][26]).decode(encoding='utf-8')

        if not len(data[i][27]):
            estim_date = None
        else:
            #estim_date = datetime.datetime.strptime(bytearray(data[i][27]).decode(encoding='utf-8'), "%d.%m.%Y %H:%M:%S")
            estim_date = parser.parse(bytearray(data[i][27]).decode(encoding='utf-8'))

        bp_decrip = bytearray(data[i][28]).decode(encoding='utf-8')
        bp_file = bytearray(data[i][29]).decode(encoding='utf-8')
        photos = bytearray(data[i][30]).decode(encoding='utf-8')


        try:
            L_InnPrj.objects.create(btx_id = btx_id,\
                                prj_name = prj_name,\
                                detail_page_url = detail_page_url,\
                                preview_picture = preview_picture,\
                                preview_text = preview_text,\
                                detail_picture = detail_picture,\
                                detail_text = detail_text,\
                                create_date = create_date,\
                                author = author,\
                                industry = industry,\
                                company = company,\
                                tpp = tpp,\
                                prj_title = prj_title,\
                                fax = fax,\
                                phone = phone,\
                                email = email,\
                                tech_info = tech_info,\
                                deleted = deleted,\
                                keywords = keywords,\
                                private_name = private_name,\
                                private_resume = private_resume,\
                                country = country,\
                                site = site,\
                                project_name = project_name,\
                                project_point = project_point,\
                                target_community = target_community,\
                                prj_sum = prj_sum,\
                                estim_date = estim_date,\
                                bp_decrip = bp_decrip,\
                                bp_file = bp_file,\
                                photos = photos)
            count += 1
        except:
            print('Milestone: ', i+1)
            print(btx_id, '##', prj_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Innovative Projects were migrated from CSV into DB!')

def innprj_DB_DB(request):
    '''
        Reload Innovative Projects from buffer DB table LEGACY_DATA_L_INNPRJ into TPP DB
    '''
    img_root = 'c:' #additional path to images
    time1 = datetime.datetime.now()
    print('Loading Innovative Projects from buffer DB into TPP DB...')
    qty = L_InnPrj.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    i = 0
    prj_lst = L_InnPrj.objects.filter(completed=False).all()
    for leg_prj in prj_lst:
        #set create_user (owner) for the Innovative Project
        if leg_prj.author:
            try:
                l_user = L_User.objects.get(btx_id=leg_prj.author)
                create_usr = User.objects.get(pk=l_user.tpp_id)
            except:
                create_usr = User.objects.get(pk=1)
        else:
            create_usr = User.objects.get(pk=1)

        try:
            prj = InnovationProject.objects.create(title='INN_PROJECT_LEG_ID:'+leg_prj.btx_id,
                                                  create_user=create_usr)
        except:
            print(leg_prj.btx_id, '##', leg_prj.prj_name, '##', ' Count: ', i)
            i += 1
            continue
        '''
        if len(leg_prj.preview_picture):
            img_small_path = add(img_root + leg_prj.preview_picture)
        else:
            img_small_path = ''
        if len(leg_prj.detail_picture):
            img_detail_path = add(img_root + leg_prj.detail_picture)
        else:
            img_detail_path = ''
        '''
        file_path = addFile(leg_prj.bp_file)

        attr = {
                'NAME': leg_prj.prj_name,
                'PRODUCT_NAME': leg_prj.prj_title,
                'COST': 0,
                #'CURRENCY': '',
                'TARGET_AUDIENCE': leg_prj.target_community,
                'RELEASE_DATE': leg_prj.estim_date,
                'SITE_NAME': leg_prj.site,
                'KEYWORD': leg_prj.keywords,
                'DETAIL_TEXT': leg_prj.detail_text,
                'BUSINESS_PLAN': leg_prj.bp_decrip,
                'DOCUMENT_1': file_path,
                }

        trans_real.activate('ru') #activate russian locale
        res = prj.setAttributeValue(attr, create_usr)
        trans_real.deactivate() #deactivate russian locale
        if res:
            leg_prj.tpp_id = prj.pk
            leg_prj.completed = True
            leg_prj.save()
        else:
            print('Problems with Attributes adding!')
            i += 1
            continue

        # create relationship type=Dependence with business entity
        try:
            leg_ent = L_Company.objects.get(btx_id=leg_prj.company)
            b_entity = Company.objects.get(pk=leg_ent.tpp_id)
            Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
        except:
            try:
                leg_ent = L_TPP.objects.get(btx_id=leg_prj.tpp)
                b_entity = Tpp.objects.get(pk=leg_ent.tpp_id)
                Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
            except:
                try:
                    leg_ent = L_User.objects.get(btx_id=leg_prj.author)
                    usr = User.objects.get(pk=leg_ent.tpp_id)
                    b_entity = Cabinet.objects.get(user=usr.pk)
                    Relationship.objects.create(parent=b_entity, type='dependence', child=prj, create_user=create_usr)
                except:
                    i += 1
                    continue

        #attache gallery to Innovative Project

        if len(leg_prj.photos): #create relationship with Gallery
            pic_lst = leg_prj.photos.split('#')
            for pic in pic_lst:
                try:
                    gal = Gallery.objects.create(title='GALLERY_FOR_INN_PROJECT_ID:'+leg_prj.btx_id, create_user=create_usr)
                except:
                    continue

                gal.photo = add(img_root + pic)
                # create relationship
                try:
                    Relationship.objects.create(parent=prj, type='dependence', child=gal, create_user=create_usr)
                    print('Relationship between Innovative Project and Gallery was created! Project ID:', prj.pk)
                except:
                    print('Can not create relationship! Project ID:', prj.pk)
                    continue

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Innovative Projects were migrated from buffer DB into TPP DB!')

def pages2comp_CSV_DB(request):
    '''
        Reload Companies' Additional Pages data from prepared CSV file named pages2comp_legacy.csv
        into buffer DB table LEGACY_DATA_L_PAGES2COMP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading Company additional pages from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\pages2comp_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        page_name = bytearray(data[i][1]).decode(encoding='utf-8')
        page_text = bytearray(data[i][2]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()

        try:
            L_Pages2Comp.objects.create(btx_id = btx_id,\
                                page_name = page_name,\
                                page_text = page_text)
            count += 1
        except:
            print('Milestone: ', i+1)
            print(btx_id, '##', page_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Company additional pages were migrated from CSV into DB!')

def pages2comp_DB_DB(request):
    '''
        Reload Company Additional Pages from buffer DB table LEGACY_DATA_L_PAGES2COMP into TPP DB
    '''
    time1 = datetime.datetime.now()
    print('Loading Company additional pages from buffer DB into TPP DB...')
    qty = L_Pages2Comp.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    i = 0
    pgs_lst = L_Pages2Comp.objects.filter(completed=False).all()
    create_usr = User.objects.get(pk=1)
    for leg_pgs in pgs_lst:
        try:
            leg_comp = L_Company.objects.get(btx_id=leg_pgs.btx_id)
            comp = Company.objects.get(pk=leg_comp.tpp_id)
        except:
            print('Could not find Company for this Additional Page. Company btx_id:', leg_pgs.btx_id)
            i += 1
            continue

        try:
            page = AdditionalPages.objects.create(title='ADD_PAGE_COMPANY_ID:'+str(comp.pk), create_user=create_usr)
        except:
            print(leg_pgs.btx_id, '##', leg_pgs.page_name, '##', ' Count: ', i)
            i += 1
            continue

        attr = {
                'NAME': leg_pgs.page_name,
                'DETAIL_TEXT': leg_pgs.page_text,
                }

        trans_real.activate('ru') #activate russian locale
        res = page.setAttributeValue(attr, create_usr)
        trans_real.deactivate() #deactivate russian locale
        if res:
            leg_pgs.completed = True
            leg_pgs.save()
        else:
            print('Problems with Attributes adding!')
            i += 1
            continue

        # create relationship type=Dependence with business entity
        try:
            Relationship.objects.create(parent=comp, type='dependence', child=page, create_user=create_usr)
        except:
            print('Can not create relationship for additional page. Page will delete.')
            page.delete()
            i += 1
            continue

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('Company additional pages were migrated from buffer DB into TPP DB!')

def pages2tpp_CSV_DB(request):
    '''
        Reload TPPs' Additional Pages data from prepared CSV file named pages2tpp_legacy.csv
        into buffer DB table LEGACY_DATA_L_PAGES2TPP
    '''
    time1 = datetime.datetime.now()
    #Upload from CSV file into buffer table
    print('Loading Company additional pages from CSV file into buffer table...')
    csv.field_size_limit(4000000)
    with open('c:\\data\\pages2tpp_legacy.csv', 'r') as f:
        reader = csv.reader(f, delimiter=';')
        data = [row for row in reader]

    count = 0
    bad_count = 0
    sz = len(data)
    for i in range(0, sz, 1):
        sz1 = len(data[i])
        for k in range(0, sz1, 1):
            data[i][k] = base64.standard_b64decode(data[i][k])

        if sz1 == 0:
            print('The row# ', i+1, ' is wrong!')
            bad_count += 1
            continue

        btx_id = bytearray(data[i][0]).decode(encoding='utf-8')
        page_name = bytearray(data[i][1]).decode(encoding='utf-8')
        page_text = bytearray(data[i][2]).decode(encoding='utf-8').replace("&quot;", '"').\
                                replace("quot;", '"').replace("&amp;", "&").strip()

        try:
            L_Pages2Tpp.objects.create(btx_id = btx_id,\
                                page_name = page_name,\
                                page_text = page_text)
            count += 1
        except:
            print('Milestone: ', i+1)
            print(btx_id, '##', page_name, '##', ' Count: ', i+1)
            continue

        print('Milestone: ', i+1)

    print('Done. Quantity of processed strings: ', i+1, ". Into buffer DB were added: ", count, ". Bad Qty: ", bad_count)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPP additional pages were migrated from CSV into DB!')

def pages2tpp_DB_DB(request):
    '''
        Reload TPP Additional Pages from buffer DB table LEGACY_DATA_L_PAGES2TPP into TPP DB
    '''
    time1 = datetime.datetime.now()
    print('Loading TPP additional pages from buffer DB into TPP DB...')
    qty = L_Pages2Tpp.objects.filter(completed=True).count()
    print('Before already were processed: ', qty)
    i = 0
    pgs_lst = L_Pages2Tpp.objects.filter(completed=False).all()
    create_usr = User.objects.get(pk=1)
    for leg_pgs in pgs_lst:
        try:
            leg_tpp = L_TPP.objects.get(btx_id=leg_pgs.btx_id)
            tpp = Tpp.objects.get(pk=leg_tpp.tpp_id)
        except:
            print('Could not find TPP for this Additional Page. TPP btx_id:', leg_pgs.btx_id)
            i += 1
            continue

        try:
            page = AdditionalPages.objects.create(title='ADD_PAGE_COMPANY_ID:'+str(tpp.pk), create_user=create_usr)
        except:
            print(leg_pgs.btx_id, '##', leg_pgs.page_name, '##', ' Count: ', i)
            i += 1
            continue

        attr = {
                'NAME': leg_pgs.page_name,
                'DETAIL_TEXT': leg_pgs.page_text,
                }

        trans_real.activate('ru') #activate russian locale
        res = page.setAttributeValue(attr, create_usr)
        trans_real.deactivate() #deactivate russian locale
        if res:
            leg_pgs.completed = True
            leg_pgs.save()
        else:
            print('Problems with Attributes adding!')
            i += 1
            continue

        # create relationship type=Dependence with business entity
        try:
            Relationship.objects.create(parent=tpp, type='dependence', child=page, create_user=create_usr)
        except:
            print('Can not create relationship for additional page. Page will delete.')
            page.delete()
            i += 1
            continue

        i += 1
        print('Milestone: ', qty + i)

    print('Done. Quantity of processed strings:', qty + i)
    time2 = datetime.datetime.now()
    time = time2-time1
    print('Elapsed time:', time)
    return HttpResponse('TPP additional pages were migrated from buffer DB into TPP DB!')
