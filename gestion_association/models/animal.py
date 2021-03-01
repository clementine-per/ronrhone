from datetime import timedelta
from enum import Enum

from django.db import models
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.famille import Famille
from gestion_association.models.person import Person


class TestResultChoice(Enum):
    NT = "Non testé"
    POSITIVE = "Positif"
    NEGATIVE = "Négatif"


class SexeChoice(Enum):
    F = "Femelle"
    M = "Mâle"


class TypeChoice(Enum):
    CHAT = "Chat"
    CHIEN =  "Chien"


class StatutAnimal(Enum):
    A_ADOPTER = "A l'adoption"
    ADOPTION = "En cours d'adoption"
    SOCIA =  "Sociabilisation"
    ADOPTE = "Adopté"
    ADOPTE_DEFINITIF = "Adopté définitivement"
    QUARANTAINE = "Quarantaine"
    SOIN = "En soin"
    SEVRAGE = "En sevrage"
    PERDU = "Perdu"
    DECEDE = "Décédé"
    RENDU = "Rendu à ses propriétaires"


statuts_association = [StatutAnimal.A_ADOPTER.name, StatutAnimal.ADOPTION.name, StatutAnimal.SOCIA.name,
                       StatutAnimal.ADOPTE.name, StatutAnimal.QUARANTAINE.name, StatutAnimal.SOIN.name,
                       StatutAnimal.SEVRAGE.name]


class Presence(Enum):
    BAS = "Bas"
    NORMAL = "Normal"
    ELEVE = "Elevé"


class TrancheAge(Enum):
    CHATON = "Chaton"
    ADULTE = "Adulte"
    SENIOR = "Sénior"


class Preference(models.Model):
    sociabilisation = models.CharField(max_length=3, default="NON",
                                       verbose_name="Sociabilisation",
                                       choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    exterieur = models.CharField(max_length=3, default="NON",
                                       verbose_name="Extérieur",
                                       choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    quarantaine = models.CharField(max_length=3, default="NON",
                                 verbose_name="Quarantaine",
                                 choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    biberonnage = models.CharField(max_length=3, default="NON",
                                   verbose_name="Biberonnage",
                                   choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    presence = models.CharField(max_length=10, blank=True, default="BAS",
                                   verbose_name="Niveau de présence",
                                   choices=[(tag.name, tag.value) for tag in Presence])


class Animal(models.Model):
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    nom = models.CharField(max_length=150)
    circonstances = models.CharField(max_length=150)
    date_naissance = models.DateField(
        verbose_name="Date de naissance", null=True, blank=True
    )
    date_arrivee = models.DateField(
        verbose_name="Date de prise en charge", null=True, blank=True
    )
    sexe = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )
    type = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
    )
    sterilise = models.CharField(max_length=3,
                                     verbose_name="Stérilisé(e)",
                                    choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    identification = models.CharField(max_length=150,
                                     verbose_name="Numéro d'identification", blank=True)
    lien_icad = models.URLField(max_length=150,
                                      verbose_name="Lien ICAD", blank=True)
    fiv = models.CharField(
        max_length=30,
        verbose_name="FIV",
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
    )
    felv = models.CharField(
        max_length=30,
        verbose_name="FELV",
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
    )
    vaccine = models.CharField(max_length=3,
                                    verbose_name="Vacciné(e)",
                                    choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    date_dernier_vaccin = models.DateField(
        verbose_name="Date du dernier rappel de vaccin", null=True, blank=True
    )
    date_prochain_vaccin = models.DateField(
        verbose_name="Date du prochain rappel de vaccin", null=True, blank=True
    )
    date_sterilisation = models.DateField(
        verbose_name="Date de stérilisation", null=True, blank=True
    )
    date_vermifuge = models.DateField(
        verbose_name="Date du dernier vermifuge", null=True, blank=True
    )
    date_parasite = models.DateField(
        verbose_name="Date d'administration de l'anti parasite", null=True, blank=True
    )
    statut = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value) for tag in StatutAnimal],
    )
    date_mise_adoption = models.DateField(
        verbose_name="Date de mise à l'adoption", null=True, blank=True
    )
    adoptant = models.ForeignKey(
        Person,
        verbose_name="Adoptant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    commentaire_sante = models.CharField(max_length=1000, blank=True)
    preference = models.OneToOneField(Preference, on_delete=models.PROTECT, blank=True, null=True)
    animaux_lies = models.ManyToManyField('self', verbose_name="Animaux liés", blank=True)
    tranche_age = models.CharField(max_length=10, blank=True,
                                   verbose_name="Tranche d'âge",
                                   choices=[(tag.name, tag.value) for tag in TrancheAge])
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        # Au premier enregistrement en base, on initialise les préférences
        if self._state.adding:
            preference = Preference.objects.create()
            self.preference = preference
            preference.save()
            # Déterminer la tranche d'age à partir de la date de naissance
            if (self.date_naissance):
                today = timezone.now().date()
                six_months = today - timedelta(days=6*30)
                senior = today - timedelta(days=30*12*10)
                date_naissance = self.date_naissance
                if date_naissance > six_months:
                    self.tranche_age = TrancheAge.CHATON.name
                elif date_naissance > senior:
                    self.tranche_age = TrancheAge.ADULTE.name
                else:
                    self.tranche_age = TrancheAge.SENIOR.name

        return super(Animal,self).save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_vaccin_str(self):
        if self.date_dernier_vaccin:
            return (
                "Oui "
                + " (dernier rappel le "
                + self.date_dernier_vaccin.strftime("%d/%m/%Y")
                + " )"
            )
        elif self.vaccine == OuiNonChoice.OUI.name:
            return "Oui"
        else:
            return "Non"

    def get_sterilisation_str(self):
        if self.date_sterilisation:
            return (
                "Oui"
                + " (en date du "
                + self.date_sterilisation.strftime("%d/%m/%Y")
                + " )"
            )
        elif self.sterilise == OuiNonChoice.OUI.name:
            return "Oui"
        else:
            return "Non"


class Adoption(models.Model):
    date = models.DateField(verbose_name="Date de l'adoption")
    acompte = models.CharField(max_length=3,
                                    verbose_name="Acompte versé",
                                    choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    montant = models.DecimalField(
        verbose_name="Montant à payer", max_digits=7, decimal_places=2,
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
        null=True, verbose_name="Nombre de jours entre mise à l'adoption et adoption effective"
    )
    animal = models.OneToOneField(Animal, on_delete=models.PROTECT)
    pre_visite = models.CharField(max_length=3,
                                    verbose_name="Visite pré-adoption",
                                    choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    visite_controle = models.CharField(max_length=3,
                                    verbose_name="Visite de contrôle (2 mois)",
                                    choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    personne_visite = models.ForeignKey(
        Person,
        verbose_name="Personne ayant effectué les visites",
        on_delete=models.PROTECT,
        related_name="visites_adotion",
        null=True,
        blank=True,
    )
    date_visite = models.DateField(verbose_name="Date de la visite de contrôle", null=True, blank=True)
    commentaire = models.CharField(max_length=1000, blank=True)
    annule = models.BooleanField(default=False,
                                 verbose_name="Adoption annulée")


    def save(self, *args, **kwargs):
        # Calcul du statut de l'animal
        if (self.visite_controle):
            self.animal.statut = StatutAnimal.ADOPTE_DEFINITIF.name
        else:
            if self.date >= timezone.now().date():
                self.animal.statut = StatutAnimal.ADOPTION.name
            else:
                self.animal.statut = StatutAnimal.ADOPTE.name
        self.animal.save()
        return super(Adoption,self).save(*args, **kwargs)