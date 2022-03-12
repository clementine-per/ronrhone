import sys

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from enum import Enum

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import TypeVaccinChoice


class TypeVisiteVetoChoice(Enum):
    VAC_PRIMO_TC = "Primo vaccination TC"
    VAC_PRIMO_TCL = "Primo vaccination TCL"
    VAC_RAPPEL_TC = "Rappel vaccination TC"
    VAC_RAPPEL_TCL = "Rappel vaccination TCL"
    STE = "Stérilisation"
    TESTS = "Tests FIV/FELV"
    IDE = "Identification"
    CONSULT = "Consultation"
    PACK_TC = "Identification, primo vaccination TC, Tests FIV/FELV"
    PACK_TCL = "Identification, primo vaccination TCL, Tests FIV/FELV"
    PACK_STE_TC = "Stérilisation, Identification, primo vaccination TC, Tests FIV/FELV"
    PACK_STE_TCL = "Stérilisation, Identification, primo vaccination TCL, Tests FIV/FELV"
    AUTRE = "Autre"
    CHIRURGIE = "Chirurgie"
    URGENCE = "Urgence"


class VisiteMedicale(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    date = models.DateField(verbose_name="Date de la visite")
    type_visite = models.CharField(
        max_length=30,
        verbose_name="Objet de la visite",
        choices=[(tag.name, tag.value) for tag in TypeVisiteVetoChoice],
    )
    veterinaire = models.CharField(max_length=150, blank=True)
    commentaire = models.CharField(max_length=2000, blank=True)
    montant = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2, blank=True, null=True
    )
    animaux = models.ManyToManyField("Animal", related_name="visites")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Visite {self.type_visite} le {self.date} chez {self.veterinaire}"


@receiver(m2m_changed, sender=VisiteMedicale.animaux.through)
def visite_medicale_save_action(sender, instance, **kwargs):
    # Instance est une visite médicale
    print(instance)
    sys.stdout.flush()
    if instance.type_visite in (
            TypeVisiteVetoChoice.VAC_PRIMO_TC.name,
            TypeVisiteVetoChoice.VAC_PRIMO_TCL.name,
            TypeVisiteVetoChoice.VAC_RAPPEL_TC.name,
            TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name,
            TypeVisiteVetoChoice.STE.name,
            TypeVisiteVetoChoice.PACK_TC.name,
            TypeVisiteVetoChoice.PACK_TCL.name,
            TypeVisiteVetoChoice.PACK_STE_TCL.name,
            TypeVisiteVetoChoice.PACK_STE_TC.name,
    ):
        for animal in instance.animaux.all():
            print(animal)
            sys.stdout.flush()
            if instance.type_visite in (TypeVisiteVetoChoice.STE.name,TypeVisiteVetoChoice.PACK_STE_TCL.name,
                                        TypeVisiteVetoChoice.PACK_STE_TC.name) :
                animal.sterilise = OuiNonChoice.OUI.name
                animal.date_sterilisation = instance.date
            if instance.type_visite in (TypeVisiteVetoChoice.VAC_PRIMO_TC.name,
                                          TypeVisiteVetoChoice.PACK_TC.name, TypeVisiteVetoChoice.PACK_STE_TC.name) :
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.type_vaccin = TypeVaccinChoice.TC.name
                animal.date_prochain_vaccin = instance.date + relativedelta(weeks=3)
            if instance.type_visite in (TypeVisiteVetoChoice.VAC_PRIMO_TCL.name,
                                          TypeVisiteVetoChoice.PACK_TCL.name, TypeVisiteVetoChoice.PACK_STE_TCL.name) :
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.date_prochain_vaccin = instance.date + relativedelta(weeks=3)
                animal.type_vaccin = TypeVaccinChoice.TCL.name
            if instance.type_visite == TypeVisiteVetoChoice.VAC_RAPPEL_TC.name :
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.vaccin_ok = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.type_vaccin = TypeVaccinChoice.TC.name
                animal.date_prochain_vaccin = instance.date + relativedelta(months=12)
            if instance.type_visite == TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name:
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.vaccin_ok = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.date_prochain_vaccin = instance.date + relativedelta(months=12)
                animal.type_vaccin = TypeVaccinChoice.TCL.name
            animal.save()