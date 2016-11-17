# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from usersites.models import ExternalSiteTemplate, UserSite, UserSiteTemplate, UserSiteSchemeColor
from django import forms


class UserSiteSchemeColorInline(admin.StackedInline):
    model = UserSiteSchemeColor
    extra = 2


class UserSiteTemplateAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'folder_name',)

    inlines = [ UserSiteSchemeColorInline, ]


class UserSiteAdminForm(forms.ModelForm):
    class Meta:
        model = UserSite
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(UserSiteAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['color_template'].queryset = \
            UserSiteSchemeColor.objects.filter(template=self.instance.user_template)


class UserSiteAdmin(admin.ModelAdmin):
    save_on_top = True
    form = UserSiteAdminForm
    list_display = ('site', 'organization',)

    raw_id_fields = [
            'organization',
            'site',
            'created_by',
            'updated_by'
            ]


admin.site.register(ExternalSiteTemplate, ModelAdmin)
admin.site.register(UserSite, UserSiteAdmin)
admin.site.register(UserSiteTemplate, UserSiteTemplateAdmin)
