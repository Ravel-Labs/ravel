from flask import render_template
from ravel.api import ADMINS
from flask_mail import Message
# from ravel.api import mail

# def send_email(subject, sender, recipients, html_body):
#     msg = Message(subject, sender=sender, recipients=recipients)
#     # msg.body = text_body
#     msg.html = html_body
#     mail.send(msg)

def follower_notification():
    return "true"
    # send_email("[microblog] %s is now following you!" % "Gabriel",
    #            ADMINS[0],
    #            'aboy.gabriel@outlook.com',
    #            render_template("welcome.html"))