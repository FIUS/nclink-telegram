import smtplib
import ssl
from email.mime.text import MIMEText
import mail.config as config


def resolveTicket(ticket_number, links, language="de"):
    
    is_sended=False
    smtp_ssl_host = 'smtp.stuvus.uni-stuttgart.de'
    smtp_ssl_port = 587
    username = config.username
    password = config.password
    sender = config.sender
    targets = config.targets

    formated_links = ""

    for link in links:
        formated_links += "  - "+link+"\n"

    if language == "de":
        message_body = config.message_template_beginning
    elif language == "en":
        message_body = config.message_template_beginning_english

    message_body = message_body+"\n"+formated_links

    if language == "de":
        message_body = message_body+"\n"+config.message_template_ending
    elif language == "en":
        message_body = message_body+"\n"+config.message_template_ending_english

    msg = MIMEText(message_body)
    msg['Subject'] = '[FIUSPV-'+str(ticket_number)+']'
    msg['From'] = sender
    msg['To'] = targets[0]

    context = ssl.create_default_context()

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_ssl_host, smtp_ssl_port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(username, password)
        server.sendmail(sender, targets, msg.as_string())
        is_sended=True
        print("sended")
    return is_sended

# Example
# resolveTicket(135, ["Datawarehouse, OLAP und Data-Mining: https://nextcloud.stuvus.uni-stuttgart.de/s/4qFp7rYyGemda2Z","Implementierung von Datenbanken und Informationssystemen https://nextcloud.stuvus.uni-stuttgart.de/s/KLLKqZrTffLBpHq"])
