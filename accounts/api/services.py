from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_activation_email(user, activation_link):
    # Kontext-Variablen für das Template definieren
    context = {"user": user, "activation_link": activation_link}

    # Template rendern und Plain-Text aus dem HTML erzeugen
    html_content = render_to_string("accounts/activation_email.html", context)
    text_content = strip_tags(html_content)

    # E-Mail Objekt erstellen
    subject = "Aktiviere deinen Videoflix-Account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # E-Mail versenden
    msg.send()
