# -*- encoding: utf-8 -*-
from django import forms
from b24online.models import Profile
from urllib.parse import urlparse


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('country', 'first_name', 'middle_name', 'last_name',
        'mobile_number', 'site', 'profession', 'sex', 'user_type', 'contacts',
        'co_name', 'co_slogan', 'co_description')
        widgets = {
            'sex': forms.RadioSelect,
            'user_type': forms.RadioSelect,
            'contacts': forms.Textarea,
            'co_description': forms.Textarea
        }

    birthday = forms.DateField(input_formats=["%d/%m/%Y"])
    facebook = forms.CharField(required=False)
    linkedin = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    instagram = forms.CharField(required=False)
    youtube = forms.CharField(required=False)
    gplus = forms.CharField(required=False)
    vkontakte = forms.CharField(required=False)
    odnoklassniki = forms.CharField(required=False)
    co_phone = forms.CharField(required=False)
    co_fax = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.birthday:
            self.initial['birthday'] = self.instance.birthday.strftime('%d/%m/%Y')

        self.initial['facebook'] = self.instance.facebook
        self.initial['linkedin'] = self.instance.linkedin
        self.initial['twitter'] = self.instance.twitter
        self.initial['instagram'] = self.instance.instagram
        self.initial['youtube'] = self.instance.youtube
        self.initial['gplus'] = self.instance.gplus
        self.initial['vkontakte'] = self.instance.vkontakte
        self.initial['odnoklassniki'] = self.instance.odnoklassniki
        self.initial['co_phone'] = self.instance.co_phone
        self.initial['co_fax'] = self.instance.co_fax

        self.fields['first_name'].widget.attrs.update({'class': 'text'})
        self.fields['middle_name'].widget.attrs.update({'class': 'text'})
        self.fields['last_name'].widget.attrs.update({'class': 'text'})
        self.fields['mobile_number'].widget.attrs.update({'class': 'text'})
        self.fields['site'].widget.attrs.update({'class': 'text'})
        self.fields['profession'].widget.attrs.update({'class': 'text'})
        self.fields['birthday'].widget.attrs.update({'class': 'date'})
        self.fields['contacts'].widget.attrs.update({'class': 'textarea'})
        self.fields['facebook'].widget.attrs.update({'class': 'text'})
        self.fields['linkedin'].widget.attrs.update({'class': 'text'})
        self.fields['twitter'].widget.attrs.update({'class': 'text'})
        self.fields['instagram'].widget.attrs.update({'class': 'text'})
        self.fields['youtube'].widget.attrs.update({'class': 'text'})
        self.fields['gplus'].widget.attrs.update({'class': 'text'})
        self.fields['vkontakte'].widget.attrs.update({'class': 'text'})
        self.fields['odnoklassniki'].widget.attrs.update({'class': 'text'})
        self.fields['co_phone'].widget.attrs.update({'class': 'text'})
        self.fields['co_fax'].widget.attrs.update({'class': 'text'})

        self.fields['co_name'].widget.attrs.update({'class': 'text'})
        self.fields['co_slogan'].widget.attrs.update({'class': 'text'})
        self.fields['co_description'].widget.attrs.update({'class': 'textarea'})

    def clean_site(self):
        url = self.cleaned_data.get('site', False)

        if url:
            p = urlparse(url, 'http')
            netloc = p.netloc or p.path
            path = p.path if p.netloc else ''

            if not netloc.startswith('www.'):
                netloc = 'www.' + netloc

            return(p.geturl().replace('///', '//'))


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)

