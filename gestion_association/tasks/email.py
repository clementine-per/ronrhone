from datetime import timedelta

from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from gestion_association.models.animal import Animal, statuts_association

sender = settings.EMAIL_HOST_USER
receiver = settings.EMAIL_HOST_USER

@background()
def send_email_for_vaccines():

    today = timezone.now().date()
    interval_10 = today + timedelta(days=10)

    # Vaccins à faire (10 jours)
    vaccins = (
        Animal.objects.filter(inactif=False)
            .filter(statut__in=statuts_association)
            .filter(date_prochain_vaccin__gte=today)
            .filter(date_prochain_vaccin__lte=interval_10)
    )
    # Vaccins dépassés
    vaccins_retard = (
        Animal.objects.filter(inactif=False)
            .filter(statut__in=statuts_association)
            .filter(date_prochain_vaccin__lte=today)
    )

    message = render_to_string("gestion_association/emails/vaccines_email.html", locals())
    send_mail(
        "[Alerte Application] Rappels de vaccins",
        message,
        sender,
        [receiver],
        fail_silently=False,
        html_message=message
    )