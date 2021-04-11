from django.db import models
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import (
    StatutAnimal,
    Animal,
    TypeChoice,
    SexeChoice,
    TrancheAge,
)
from gestion_association.models.person import Person


class Adoption(models.Model):
    date = models.DateField(verbose_name="Date de l'adoption")
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
        max_length=3,
        verbose_name="Visite de contrôle (2 mois)",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
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

    def save(self, *args, **kwargs):
        # Calcul du statut de l'animal
        if self.date >= timezone.now().date():
            self.animal.statut = StatutAnimal.ADOPTION.name
        else:
            self.animal.statut = StatutAnimal.ADOPTE.name
        self.animal.save()
        return super(Adoption, self).save(*args, **kwargs)


class BonSterilisation(models.Model):
    adoption = models.OneToOneField(Adoption, on_delete=models.PROTECT)
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
    date_utilisation = models.DateField(
        verbose_name="Date d'utilisation", null=True, blank=True
    )

    def __str__(self):
        result = "Bon de stérilisation "
        if self.envoye == "NON":
            return result + "demandé mais non envoyé."
        if self.utilise == "NON":
            return result + "a utiliser avant le " + self.date_max.strftime("%d/%m/%Y")
        if self.date_utilisation:
            return result + "utilisé le " + self.date_utilisation.strftime("%d/%m/%Y")
        return result + "utilisé."


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
    montant = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2
    )

    def __str__(self):
        return "Tarif adoption pour " + self.type_animal


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

    montant = models.DecimalField(
        verbose_name="Montant", max_digits=7, decimal_places=2
    )

    def __str__(self):
        return "Tarif bon de stérilisation pour " + self.type_animal
