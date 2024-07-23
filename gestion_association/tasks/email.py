from datetime import timedelta

from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from gestion_association.models.animal import Animal, statuts_association
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

asso_email = settings.EMAIL_HOST_USER


@background()
def send_email_for_upcoming_vaccines():

    today = timezone.now().date()
    interval_6 = today + timedelta(days=6)
    interval_7 = today + timedelta(days=7)
    interval_2 = today + timedelta(days=2)
    interval_3 = today + timedelta(days=3)

    # Vaccins à faire (7 jours)
    jours = "7"
    vaccins = (
        Animal.objects.filter(inactif=False)
            .filter(statut__in=statuts_association)
            .filter(date_prochain_vaccin__gte=today)
            .filter(date_prochain_vaccin__lte=interval_7)
            .filter(date_prochain_vaccin__gte=interval_6)
    )
    for animal in vaccins:
        # Send email only to family if there is one
        if animal.famille:
            # don't send to test emails
            if not animal.famille.personne.email == "test@test.fr":
                logger.info("Envoi mail rappel vaccin 7 jours à " + animal.famille.personne.email)
                message = render_to_string("gestion_association/emails/upcoming_vaccines_email.html", locals())
                send_mail(
                    "[Alerte Ron'Rhône] Rappel de vaccin " + animal.nom,
                    message,
                    asso_email,
                    [animal.famille.personne.email],
                    fail_silently=False,
                    html_message=message
                )
    # Vaccins à faire (3 jours)
    jours = "3"
    vaccins = (
        Animal.objects.filter(inactif=False)
            .filter(statut__in=statuts_association)
            .filter(date_prochain_vaccin__gte=today)
            .filter(date_prochain_vaccin__lte=interval_3)
            .filter(date_prochain_vaccin__gte=interval_2)
    )
    for animal in vaccins:
        # Send email only to family if there is one
        if animal.famille:
            # don't send to test emails
            if not animal.famille.personne.email == "test@test.fr":
                logger.info("Envoi mail rappel vaccin 3 jours à " + animal.famille.personne.email)
                message = render_to_string("gestion_association/emails/upcoming_vaccines_email.html", locals())
                send_mail(
                    "[Alerte Ron'Rhône] Rappel de vaccin " + animal.nom,
                    message,
                    asso_email,
                    [animal.famille.personne.email],
                    fail_silently=False,
                    html_message=message
                )


@background()
def send_email_for_past_vaccines():

    today = timezone.now().date()
    # Vaccins dépassés
    vaccins_retard = (
        Animal.objects.filter(inactif=False)
            .filter(statut__in=statuts_association)
            .filter(date_prochain_vaccin__lte=today)
    )
    for animal in vaccins_retard.all():
        # Send email only to family if there is one
        if animal.famille:
            # don't send to test emails
            if not animal.famille.personne.email == "test@test.fr":
                logger.info("Envoi mail rappel vaccin dépassé à " + animal.famille.personne.email)
                message = render_to_string("gestion_association/emails/past_vaccines_email.html", locals())
                send_mail(
                    "[Alerte Ron'Rhône] Date de rappel de vaccin dépassée pour " + animal.nom,
                    message,
                    asso_email,
                    [animal.famille.personne.email],
                    fail_silently=False,
                    html_message=message
                )