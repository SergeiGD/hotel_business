import smtplib
from email.message import EmailMessage
from hotel_business_module.settings import settings


def send_email(subject: str, content: str, send_to: str):
    """
    Отправка писем
    :param subject: тема письма
    :param content: контент письма
    :param send_to: получатель
    :return:
    """
    msg = EmailMessage()
    msg.set_content(content)

    msg['From'] = settings.EMAIL_USER
    msg['To'] = send_to
    msg['Subject'] = subject

    server = smtplib.SMTP_SSL('smtp.yandex.com')
    server.set_debuglevel(1)
    server.ehlo(settings.EMAIL_USER)
    server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
    server.auth_plain()
    server.send_message(msg)
    server.quit()
