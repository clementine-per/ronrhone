from decimal import Decimal
from enum import Enum
from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import (
    Animal,
    SexeChoice,
    StatutAnimal,
    TrancheAge,
    TypeChoice,
)
from gestion_association.models.famille import StatutFamille, StatutAccueil
from gestion_association.models.person import Person

class OuiNonVisiteChoice(Enum):
    OUI = "Oui"
    NON = "Non"
    VACCIN = "Attente vaccin"
    ALIMENTAIRE = "Transition alimentaire"



class Adoption(models.Model):
    date = models.DateField(verbose_name="Date de l'adoption",null=True,
        blank=True,)
    montant = models.DecimalField(
        verbose_name="Montant à payer",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    montant_restant = models.DecimalField(
        verbose_name="Montant restant à payer",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    adoptant = models.ForeignKey(Person, on_delete=models.PROTECT)
    nb_jours = models.IntegerField(
        null=True,
        verbose_name="Nombre de jours entre mise à l'adoption et adoption effective",
    )
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    pre_visite = models.CharField(
        max_length=3,
        verbose_name="Visite pré-adoption",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    visite_controle = models.CharField(
        max_length=15,
        verbose_name="Visite de contrôle (2 mois)",
        choices=[(tag.name, tag.value) for tag in OuiNonVisiteChoice],
    )
    personne_visite = models.ForeignKey(
        Person,
        verbose_name="Personne ayant effectué les visites",
        on_delete=models.PROTECT,
        related_name="visites_adotion",
        null=True,
        blank=True,
    )
    date_visite = models.DateField(
        verbose_name="Date de la visite de contrôle", null=True, blank=True
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    annule = models.BooleanField(default=False, verbose_name="Adoption annulée")
    acompte_verse = models.CharField(
        max_length=3,
        verbose_name="Acompte versé",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )

    def __str__(self):
        return f"Adoption de {self.animal.nom} par {str(self.adoptant)}"

    def save(self, *args, **kwargs):
        if not self.annule:
            # Maj statut lors de la création de l'adoption
            if self._state.adding:
                # Annulation des adoptions précédentes
                if self.animal.adoption_set and self.animal.adoption_set.all().count() > 0 :
                    for adoption in self.animal.adoption_set.all():
                        adoption.annule = True
                        adoption.save()
                self.animal.statut = StatutAnimal.ADOPTION.name
                self.animal.adoptant = self.adoptant
                self.animal.save()
                self.adoptant.is_adoptante = True
                self.adoptant.save()

                if not self.date_visite and self.date :
                    self.date_visite = self.date + relativedelta(months=2)
            # # Maj statut si adoption payée et retirer de la FA
            if self.visite_controle == OuiNonChoice.NON.name and self.pre_visite == OuiNonChoice.OUI.name and (not self.montant_restant or self.montant_restant == Decimal(0)):
                self.animal.statut = StatutAnimal.ADOPTE.name
                if self.animal.famille:
                    famille = self.animal.famille
                    for accueil in famille.accueil_set.filter(date_fin__isnull=True).filter(animal__pk=self.animal.id).all():
                        accueil.date_fin = timezone.now().date()
                        accueil.statut = StatutAccueil.TERMINE.name
                        accueil.save()
                    self.animal.famille = None
                    self.animal.save()
        return super(Adoption, self).save(*args, **kwargs)


class BonSterilisation(models.Model):
    adoption = models.OneToOneField(Adoption, on_delete=models.PROTECT, related_name="bon")
    date_max = models.DateField(verbose_name="Date d'expiration")
    envoye = models.CharField(
        max_length=3,
        verbose_name="Bon envoyé",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    utilise = models.CharField(
        max_length=3,
        verbose_name="Bon utilisé",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    date_utilisation = models.DateField(verbose_name="Date d'utilisation", null=True, blank=True)
    veterinaire = models.CharField(max_length=100, blank=True)

    def __str__(self):
        result = "Bon de stérilisation "
        if self.veterinaire:
            result += f"pour {self.veterinaire} "
        if self.envoye == "NON":
            return f"{result}demandé mais non envoyé."
        if self.utilise == "NON":
            return f"{result}a utiliser avant le " + self.date_max.strftime("%d/%m/%Y")
        if self.date_utilisation:
            return f"{result}utilisé le " + self.date_utilisation.strftime("%d/%m/%Y")
        return f"{result}utilisé."

    def save(self, *args, **kwargs):
        # # Maj statut stérilisation si bon utilisé
        if self.utilise == "OUI":
            self.adoption.animal.sterilise = self.utilise
            self.adoption.animal.save()
        return super(BonSterilisation, self).save(*args, **kwargs)


class TarifAdoption(models.Model):
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
    )
    sexe = models.CharField(
        max_length=30,
        verbose_name="Sexe",
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )
    sterilise = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Stérilisé",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    tranche_age = models.CharField(
        max_length=10,
        verbose_name="Tranche d'âge",
        choices=[(tag.name, tag.value) for tag in TrancheAge],
    )
    vaccin_ok = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Vaccins à jour",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    montant = models.DecimalField(verbose_name="Montant", max_digits=7, decimal_places=2)

    def __str__(self):
        return f"Tarif adoption pour {self.type_animal}"


class TarifBonSterilisation(models.Model):
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
    )
    sexe = models.CharField(
        max_length=30,
        verbose_name="Sexe",
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )

    montant = models.DecimalField(verbose_name="Montant", max_digits=7, decimal_places=2)

    def __str__(self):
        return f"Tarif bon de stérilisation pour {self.type_animal}"
