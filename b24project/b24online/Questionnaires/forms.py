# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory

from b24online import InvalidParametersError
from b24online.models import (Questionnaire, Question, Answer, B2BProduct,
                              Recommendation)
from centerpokupok.models import B2CProduct

logger = logging.getLogger(__name__)


class QuestionnaireForm(forms.ModelForm):

    item_label = _('Questionnaire for')

    class Meta:
        model = Questionnaire
        fields = ['name', 'short_description', 'description', 'image']

    def __init__(self, request, content_type_id=None, item_id=None, 
                 *args, **kwargs):
        cls = type(self)
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.item
        else:
            try:
                self._content_type = ContentType.objects.get(
                    pk=content_type_id
                )
            except ContentType.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid ContentType ID')
                )
            else:
                model_class = self._content_type.model_class()
                try:
                    self.item = model_class.objects.get(pk=item_id)
                except model_class.DoesNotExist:
                    raise InvalidParametersError(
                        _('Invalid Object ID')
                    )

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.content_type = self._content_type
            self.instance.item = self.item
            self.instance.created_by = self.request.user
        return super(QuestionnaireForm, self).save(*args, **kwargs)


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['question_text', ]

    def __init__(self, request, item_id=None, *args, **kwargs):
        cls = type(self)
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.questionnaire
        else:
            try:
                self.item = Questionnaire.objects.get(pk=item_id)
            except Questionnaire.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid Object ID')
                )

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.questionnaire = self.item
            self.instance.created_by = self.request.user
        return super(QuestionForm, self).save(*args, **kwargs)


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = Recommendation
        fields = ['question', 'name', 'description',]

    def __init__(self, request, item_id=None, *args, **kwargs):
        cls = type(self)
        super(RecommendationForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.instance and self.instance.pk:
            self.item = self.instance.questionnaire
        else:
            try:
                self.item = Questionnaire.objects.get(pk=item_id)
            except Questionnaire.DoesNotExist:
                raise InvalidParametersError(
                    _('Invalid Object ID')
                )
        self.fields['question'].queryset = Question.objects\
            .filter(questionnaire=self.item)
        self.fields['question'].required = True
        self.fields['description'].required = True

    def save(self, *args, **kwargs):
        if self.instance.pk:
            self.instance.updated_by = self.request.user
        else:
            self.instance.questionnaire = self.item
            self.instance.created_by = self.request.user
        return super(RecommendationForm, self).save(*args, **kwargs)