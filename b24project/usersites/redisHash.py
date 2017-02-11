# -*- coding: utf-8 -*-
import pickle
from django.conf import settings
from usersites.models import UserSite
from tpp.DynamicSiteMiddleware import get_current_site
from django.core.exceptions import ImproperlyConfigured

def get_usersite_objects(typeof=None):
    obj = UsersiteHash().check()

    if not typeof:
        return obj
    else:
        u, t, o = obj
        return { 'usersite': u, 'template': t, 'organization': o}


class UsersiteHash:
    """A siple usersite hash class"""
    def __init__(self):
        self.domain = get_current_site()
        try:
            self.r = settings.REDIS_USERSITE
        except ImproperlyConfigured as e:
            raise(e)

    def check(self):
        if self.r.hget(self.domain, "usersite"):
            usersite = pickle.loads(self.r.hget(self.domain, 'usersite'))
            template = pickle.loads(self.r.hget(self.domain, 'template'))
            organization = pickle.loads(self.r.hget(self.domain, 'organization'))
        else:

            try:
                usersite = UserSite.objects.get(site__domain=self.domain)
            except UserSite.DoesNotExist as e:
                raise(e)
            else:

                u = pickle.dumps(usersite)
                t = pickle.dumps(usersite.user_template)
                o = pickle.dumps(usersite.organization)

            self.r.hmset(self.domain, {
                    "usersite": u,
                    "template": t,
                    "organization": o
                    }
                )

            template = usersite.user_template
            organization = usersite.organization

        return(usersite, template, organization)

    def flush(self, instance):
        site = instance.site.domain
        try:
            self.r.delete(site)
        except ImproperlyConfigured as e:
            raise(e)




