from flask import render_template, abort
from api import ADMINS_FROM_EMAIL_ADDRESS, mail, Q, Job
from flask_mail import Message


def send_email(title, sender, receivers, html_body, sound_file):
    msg = Message(title, sender=sender, recipients=receivers)
    msg.html = html_body
    if sound_file:
        msg.attach("results.wav", "audio/wav", sound_file)
    mail.send(msg)


'''
    Emails can either be custom by definition of the caller
    or classified by the template_type.
    Required Fields
        template_type Required, determines the template text values
        user_to_email_address Required,
        defines where the service will be sending the email
'''


def email_proxy(
    template_type,
    user_to_email_address,
    user_name="",
    title="",
    intro="",
    broadcast_msg_one="",
    broadcast_msg_two="",
    button_title="",
    button_link="",
    sound_file=""
):

    try:
        '''
            Default email values
        '''
        template_name = "broadcast.html"

        default_intro = f"Hey {user_name}," if user_name \
                        else "Greetings from Ravel,"

        button_link = button_link or "google.com"
        intro = intro or default_intro
        # Documentation requires a list of emails
        if not isinstance(user_to_email_address, list):
            user_to_email_address = [user_to_email_address]

        '''
            Reconfigureation of the base template

            Thought: we might want to return an error
            for some templates if broadcast_msg_* are not passed...
        '''
        if template_type == "welcome":
            title = title or "Greetings from Ravel"
            broadcast_msg_one = broadcast_msg_one or "Ravel wants to welcome"\
                " you to the platform."
            broadcast_msg_two = broadcast_msg_two or "Here you"\
                " can upload tracks and configure your music with trackouts!"
            button_title = button_title or "Lets Get Started"
        elif template_type == "broadcast":
            title = title or "Ravel Update"
            broadcast_msg_one = broadcast_msg_one or "We are"\
                " excited to provide the best service."
            broadcast_msg_two = broadcast_msg_two or "Let us know"\
                " how we can improve!"
            button_title = button_title or "Check it out"
        elif template_type == "status":
            title = title or "Track Status"
            broadcast_msg_one = broadcast_msg_one or "Our services"\
                " are spinning fast to process your files."
            broadcast_msg_two = broadcast_msg_two or "Check it out later"
            # TODO Download link and conditional html for download button
            button_title = button_title or "Download"
            custom_url = button_link or "404"
        else:
            raise ValueError("Template type does not exist")

        template = render_template(
            template_name,
            title=title,
            intro=intro,
            message_part_one=broadcast_msg_one,
            message_part_two=broadcast_msg_two,
            button_title=button_title,
            custom_url=custom_url,
            sound_file=sound_file)

        '''
            Send email job out into the queue
        '''
        function_arguments = (
            title,
            ADMINS_FROM_EMAIL_ADDRESS[0],
            user_to_email_address,
            template,
            sound_file)
        email_job = Job(send_email, function_arguments)
        Q.put(email_job)
    except Exception as e:
        abort(500, e)
