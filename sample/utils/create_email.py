""" Pluggable email function. """
from collections import OrderedDict
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from sample.settings.settings import PROTOCOL, DEFAULT_FROM_EMAIL


def make_email(subject, message, to_email, template, options, request):
    """
    For sending emails.
    Build the emails parameters then render it to the templates
    for output.

    Parameters:
        subject: (str) email subject
        message: (str) message that appears below the suject/title
        to_email: (str) email address to send
        template: (str) template email
        options: (dict) dictionary of values for the email template
        request: (obj) to get the requested domain
    """
    current_site = get_current_site(request)
    emailInfo = OrderedDict()
    emailInfo['subject'] = subject
    emailInfo['message'] = message
    emailInfo['recipient_list'] = [to_email]
    emailInfo['from_email'] = DEFAULT_FROM_EMAIL
    params = {
        'email_id': to_email,
        'domain': current_site.domain,
        'protocol': PROTOCOL,
    }
    if options:
        params.update(options)
    emailInfo['html_message'] = render_to_string(template, params)
    send_mail(**emailInfo)
