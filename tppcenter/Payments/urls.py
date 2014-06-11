from django.conf.urls import patterns, url
import tppcenter.Payments.views

import tppcenter.views


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', tppcenter.Payments.views.verify_payment_status, name="verify_payment_status"),
     url(r'^advertisement/$', tppcenter.Payments.views.pay_for_adv, name="pay_for_adv"),
)