import sys
from datetime import timedelta

from background_task import background
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from gestion_association.models.animal import Animal, StatutAnimal
from gestion_association.models.famille import Famille

asso_email = settings.EMAIL_HOST_USER

statuts_association = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.PEC.name,
    StatutAnimal.SOCIA.name,
    StatutAnimal.QUARANTAINE.name,
    StatutAnimal.SOIN.name,
    StatutAnimal.SEVRAGE.name,
    StatutAnimal.ALLAITANTE.name,
]


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
            .filter(date_prochain_vaccin__lte=interval_7)
            .filter(date_prochain_vaccin__gt=interval_6)
    )
    for animal in vaccins:
        # Send email only to family if there is one
        if animal.famille:
            # don't send to test emails
            if not animal.famille.personne.email == "test@test.fr":
                print("Envoi mail rappel vaccin 7 jours à " + animal.famille.personne.email)
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
            .filter(date_prochain_vaccin__lte=interval_3)
            .filter(date_prochain_vaccin__gt=interval_2)
    )
    for animal in vaccins:
        # Send email only to family if there is one
        if animal.famille:
            # don't send to test emails
            if not animal.famille.personne.email == "test@test.fr":
                print("Envoi mail rappel vaccin 3 jours à " + animal.famille.personne.email)
                message = render_to_string("gestion_association/emails/upcoming_vaccines_email.html", locals())
                send_mail(
                    "[Alerte Ron'Rhône] Rappel de vaccin " + animal.nom,
                    message,
                    asso_email,
                    [animal.famille.personne.email],
                    fail_silently=False,
                    html_message=message
                )
    sys.stdout.flush()


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
                print("Envoi mail rappel vaccin dépassé à " + animal.famille.personne.email)
                message = render_to_string("gestion_association/emails/past_vaccines_email.html", locals())
                send_mail(
                    "[Alerte Ron'Rhône] Date de rappel de vaccin dépassée pour " + animal.nom,
                    message,
                    asso_email,
                    [animal.famille.personne.email],
                    fail_silently=False,
                    html_message=message
                )
    sys.stdout.flush()

@background()
def send_email_for_end_sevrage():
    today = timezone.now().date()
    # Chatons en fin de sevrage
    interval_2_and_half_month_ago = today - relativedelta(months=2) - timedelta(days=15)
    interval_2_and_half_month_ago_under = today - relativedelta(months=2) - timedelta(days=16)
    #Get families that need to get the alert
    animals_pk = (Animal.objects.filter(inactif=False).filter(statut="SEVRAGE")
               .filter(date_naissance__lte=interval_2_and_half_month_ago)
               .filter(date_naissance__gt=interval_2_and_half_month_ago_under)
               .values_list('pk', flat=True))
    fin_sevrage_families = Famille.objects.filter(animal__pk__in=animals_pk).distinct()
    for famille in fin_sevrage_families.all():
        # Send email for all concerned kitties
        count = 0
        names = ""
        for animal in famille.animal_set.filter(statut="SEVRAGE").all():
            count += 1
            names = names + " " + animal.nom +","
        # don't send to test emails
        if not famille.personne.email == "test@test.fr":
            print("Envoi mail fin de sevrage à " + famille.personne.email)
            message = render_to_string("gestion_association/emails/fin_sevrage_email.html", locals())
            send_mail(
                "[Alerte Ron'Rhône] Fin de période de sevrage ",
                message,
                asso_email,
                [famille.personne.email],
                fail_silently=False,
                html_message=message
            )
    sys.stdout.flush()

@background()
def send_email_for_end_quarantaine():
    today = timezone.now().date()
    interval_15_ago = today - timedelta(days=15)
    interval_15_ago_under = today - timedelta(days=16)
    #Get families that need to get the alert
    animals_pk = (Animal.objects.filter(inactif=False).filter(statut="QUARANTAINE")
                  .filter(date_arrivee__lte=interval_15_ago)
                  .filter(date_arrivee__gt=interval_15_ago_under)
                  .values_list('pk', flat=True))
    fin_quarantaine_families = Famille.objects.filter(animal__pk__in=animals_pk).distinct()
    for famille in fin_quarantaine_families.all():
        # Send email for all concerned cats
        count = 0
        names = ""
        for animal in famille.animal_set.filter(statut="QUARANTAINE").all():
            count += 1
            names = names + " " + animal.nom +","
        # don't send to test emails
        if not famille.personne.email == "test@test.fr":
            print("Envoi mail fin de quarantaine à " + famille.personne.email)
            message = render_to_string("gestion_association/emails/fin_quarantaine_email.html", locals())
            send_mail(
                "[Alerte Ron'Rhône] Fin de quarantaine ",
                message,
                asso_email,
                [famille.personne.email],
                fail_silently=False,
                html_message=message
            )
    sys.stdout.flush()