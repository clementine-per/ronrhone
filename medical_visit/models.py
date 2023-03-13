from enum import Enum

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import TypeVaccinChoice, Animal


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
    update_date = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    date = models.DateField(verbose_name="Date de la visite")
    visit_type = models.CharField(
        max_length=30,
        verbose_name="Objet de la visite",
        choices=[(tag.name, tag.value) for tag in TypeVisiteVetoChoice],
    )
    veterinary = models.CharField(max_length=150, blank=True, verbose_name="Vétérinaire")
    comment = models.CharField(max_length=2000, blank=True, verbose_name="Commentaire")
    amount = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2, blank=True, null=True
    )
    animals = models.ManyToManyField(Animal, related_name="visites",
                                     db_table="gestion_association_visitemedicale_animaux", verbose_name="Animaux")

    class Meta:
        ordering = ["-date"]
        db_table = 'gestion_association_visitemedicale'

    def __str__(self):
        return f"Visite {self.visit_type} le {self.date} chez {self.veterinary}"

    def get_amount_per_animal(self):
        if self.amount:
            nb_animals = self.animals.count()
            return self.amount/nb_animals
        return None


visit_with_sterilisation = [
    TypeVisiteVetoChoice.STE.name,
    TypeVisiteVetoChoice.PACK_STE_TCL.name,
    TypeVisiteVetoChoice.PACK_STE_TC.name
]

visit_with_initial_vaccine = [
    TypeVisiteVetoChoice.VAC_PRIMO_TC.name,
    TypeVisiteVetoChoice.VAC_PRIMO_TCL.name,
    TypeVisiteVetoChoice.PACK_TC.name,
    TypeVisiteVetoChoice.PACK_TCL.name,
    TypeVisiteVetoChoice.PACK_STE_TCL.name,
    TypeVisiteVetoChoice.PACK_STE_TC.name,
]

visit_with_full_vaccine = [
    TypeVisiteVetoChoice.VAC_RAPPEL_TC.name,
    TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name,
]

visit_with_TC_vaccine = [
    TypeVisiteVetoChoice.VAC_RAPPEL_TC.name,
    TypeVisiteVetoChoice.PACK_STE_TC.name,
    TypeVisiteVetoChoice.VAC_PRIMO_TC.name,
]

visit_with_TCL_vaccine = [
    TypeVisiteVetoChoice.VAC_RAPPEL_TCL.name,
    TypeVisiteVetoChoice.PACK_STE_TCL.name,
    TypeVisiteVetoChoice.VAC_PRIMO_TCL.name,
]

@receiver(m2m_changed, sender=VisiteMedicale.animals.through)
def visite_medicale_save_action(sender, instance, **kwargs):
    # Instance is a medical visit
    if instance.visit_type in (
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
        for animal in instance.animals.all():
            if instance.visit_type in visit_with_sterilisation:
                animal.sterilise = OuiNonChoice.OUI.name
                animal.date_sterilisation = instance.date
            if instance.visit_type in visit_with_initial_vaccine:
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.date_prochain_vaccin = instance.date + relativedelta(weeks=3)
            if instance.visit_type in visit_with_full_vaccine:
                animal.primo_vaccine = OuiNonChoice.OUI.name
                animal.vaccin_ok = OuiNonChoice.OUI.name
                animal.date_dernier_vaccin = instance.date
                animal.date_prochain_vaccin = instance.date + relativedelta(months=12)
            if instance.visit_type in visit_with_TC_vaccine:
                animal.type_vaccin = TypeVaccinChoice.TC.name
            if instance.visit_type in visit_with_TCL_vaccine:
                animal.type_vaccin = TypeVaccinChoice.TCL.name

            animal.save()
