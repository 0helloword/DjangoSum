from celery import shared_task
from django.core.mail import send_mail
from django.template import loader

from DjangoSum.settings import EMAIL_HOST_USER, SERVER_HOST, SERVER_PORT


@shared_task
def send_email(customer,receive,token):
    subject='用户激活'
    from_email=EMAIL_HOST_USER
    recipient_list=[receive,]
    data={
        'customer':customer,
        'active_url':'http://{}:{}/app/active/?token={}'.format(SERVER_HOST,SERVER_PORT,token)
    }
    html_message=loader.get_template('active.html').render(data)
    send_mail(subject, message='', from_email=from_email,html_message=html_message,recipient_list=recipient_list)