# -*- encoding: utf-8 -*-

"""
Forms for `Message` application.
"""

import logging

from django.db import transaction, IntegrityError

from django import forms
from django.utils.translation import ugettext as _
from django.utils.html import strip_tags

from b24online.models import MessageChat, Message, MessageAttachment
from b24online.utils import handle_uploaded_file

logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):

    AS_EMAIL, AS_MESSAGE = 'email', 'message'
    DELIVERY_WAYS = (
        (AS_EMAIL, _('As email')),
        (AS_MESSAGE, _('As message')),
    ) 

    delivery_way = forms.ChoiceField(
        label=_('Delivery way'), 
        choices=DELIVERY_WAYS,
        required=True,
    )
    attachment = forms.FileField(label=_('Message attachment'))

    class Meta:
        model = Message
        fields = ('organization', 'recipient', 'subject', 'content')

    def __init__(self, request, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.request = request
        self.initial['delivery_way'] = type(self).AS_MESSAGE
        self.fields['content'].required = True

    def send(self):
        """
        Send the message by means of selected way.
        """
        cls = type(self)
        logger.debug(self.data)
        logger.debug(self.files)
        logger.debug(self.cleaned_data)
        organization = self.cleaned_data.get('organization')
        recipient = self.cleaned_data.get('recipient')
        subject = self.cleaned_data.get('subject')
        content = self.cleaned_data.get('content')
        delivery_way = self.cleaned_data.get('delivery_way')
        attachment = self.cleaned_data.get('attachment')
        logger.debug(attachment)
        if delivery_way == cls.AS_MESSAGE:
            try:
                with transaction.atomic():
                    new_message_chat = MessageChat.objects.create(
                        subject=subject,
                        organization=organization,
                        status=MessageChat.OPENED,
                    )
                    new_message_chat.participants.add(self.request.user)
                    new_message = Message.objects.create(
                        subject=subject,
                        status=Message.READY,
                        recipient=recipient,
                        organization=organization,
                        sender=self.request.user,
                        chat=new_message_chat,
                        content=content,
                    )
                    if attachment:
                        new_message_attachment = MessageAttachment.objects\
                            .create(
                                file=handle_uploaded_file(attachment),
                                message=new_message,
                                created_by=self.request.user
                            )

            except IntegrityError as exc:
                raise
        else:
            if not organization.email:
                email = 'admin@tppcenter.com'
                subject = _('This message was sent to '
                    'company with id = %(organization_id)d, '
                    'subject: %(subject)s') % \
                    {'organization_id': organization.id, 
                     'subject': subject}
            else:
                email = organization.email
                subject = _('New message: %(subject)s') % {'subject': subject}

            mail = EmailMessage(
                subject, 
                content, 
                getattr(settings, 'DEFAULT_FROM_EMAIL', 
                        'noreply@tppcenter.com'), 
                [email,]
            )
            if attachment:
                mail.attach(attachment.name, attachment.read(), 
                            attachment.content_type)
            mail.send()

    def get_errors(self):
        """
        Return the errors as one string.
        """
        errors = []
        for field_name, field_messages in self.errors.items():
            errors.append('{0} : {1}' \
                . format(field_name, ', ' \
                    . join(map(lambda x: strip_tags(x), field_messages)))
                )
        return '; ' . join(errors)

    def save(self, *args, **kwargs):
        pass
