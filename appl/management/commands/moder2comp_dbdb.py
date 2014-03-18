from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import Group
from core.models import User
from appl.models import Company
from django.db.models import Q
import datetime
from legacy_data.models import *

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
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
        print('Relationships between Companies and their moderators were created!')
