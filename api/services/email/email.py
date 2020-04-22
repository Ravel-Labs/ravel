from flask import render_template, abort
from ravel.api import ADMINS, mail
from flask_mail import Message
from ravel.api.services.email.templates.welcome as welcome


def send_email(title, sender, receivers, html_body):
    msg = Message(title, sender=sender, recipients=receivers)
    msg.html = html_body
    mail.send(msg)

def email_proxy(template_type, user_to_email_address, title = ""):
    try:
        if not isinstance(user_to_email_address, list):
            user_to_email_address = list(user_to_email_address)

        if template_type is "welcome":
            title = "Welcome to Ravel"
            template = "/templates/welcome"
        else if template_type is "broadcast":
            title = title
            template = "/templates/broadcast"
        else if template_type is "status":
            title = "Track Status"
            template = "/templates/status"
        else:
            raise ValueError("Template type does not exist")
        send_email(title, ADMINS_FROM_EMAIL_ADDRESS[0], user_to_email_address, render_template(template))
    except Exception as e:
        abort(500, e)