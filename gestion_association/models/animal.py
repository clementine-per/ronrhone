from datetime import timedelta
from enum import Enum

from django.db import models
from django.utils import timezone

from gestion_association.models import OuiNonChoice, TypeChoice, PerimetreChoice
from gestion_association.models.famille import Famille, StatutAccueil
from gestion_association.models.person import Person


class TestResultChoice(Enum):
    NT = "Non testé"
    POSITIVE = "Positif"
    NEGATIVE = "Négatif"


class SexeChoice(Enum):
    F = "Femelle"
    M = "Mâle"
    NI = "Non identifié"


class TypeVaccinChoice(Enum):
    TC = "TC"
    TCL = "TCL"


class StatutAnimal(Enum):
    A_ADOPTER = "A l'adoption"
    ADOPTABLE = "Adoptable"
    ADOPTION = "En cours d'adoption"
    SOCIA = "Sociabilisation"
    ADOPTE = "Adopté"
    ADOPTE_DEFINITIF = "Adopté définitivement"
    QUARANTAINE = "Quarantaine"
    SOIN = "En soin"
    SEVRAGE = "En sevrage"
    PERDU = "Perdu"
    DECEDE = "Décédé"
    RENDU = "Rendu à ses propriétaires"
    RELACHE = "Relâché"
    PEC = "Prendre en charge"
    ALLAITANTE = "Allaitante"


statuts_association = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTION.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.PEC.name,
    StatutAnimal.SOCIA.name,
    StatutAnimal.QUARANTAINE.name,
    StatutAnimal.SOIN.name,
    StatutAnimal.SEVRAGE.name,
    StatutAnimal.ALLAITANTE.name,
]


class TypePaiementChoice(Enum):
    MENSUEL = "Mensuel"
    UNIQUE = "En une fois"


class TrancheAge(Enum):
    ENFANT = "Enfant"
    ADULTE = "Adulte"
    SENIOR = "Sénior"


class Preference(models.Model):
    sociabilisation = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Sociabilisation",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    exterieur = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Extérieur",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    quarantaine = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Quarantaine",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    biberonnage = models.CharField(
        max_length=3,
        default="NON",
        verbose_name="Biberonnage",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )

    def __str__(self):
        preferences = "Nécéssités : \n"
        if self.quarantaine == OuiNonChoice.OUI.name:
            preferences += "Quarantaine \n"
        if self.biberonnage == OuiNonChoice.OUI.name:
            preferences += "Biberonnage \n"
        if self.exterieur == OuiNonChoice.OUI.name:
            preferences += "Extérieur \n"
        if self.sociabilisation == OuiNonChoice.OUI.name:
            preferences += "Sociabilisation \n"

        return preferences

class AnimalGroup(models.Model):
    # Groupes d'animaux par foreign key sur animal
    pass


class Animal(models.Model):
    date_mise_a_jour = models.DateField(verbose_name="Date de mise à jour", auto_now=True)
    nom = models.CharField(max_length=150, unique=True)
    circonstances = models.CharField(max_length=150)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    date_arrivee = models.DateField(verbose_name="Date de prise en charge", null=True, blank=True)
    sexe = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value) for tag in SexeChoice],
    )
    type = models.CharField(
        max_length=30,
        verbose_name="Type d'animal",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
        default="CHAT",
    )
    sterilise = models.CharField(
        max_length=3,
        verbose_name="Stérilisé(e)",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    identification = models.CharField(
        max_length=150, verbose_name="Numéro d'identification", blank=True
    )
    lien_icad = models.URLField(max_length=150, verbose_name="Lien ICAD", blank=True)
    fiv = models.CharField(
        max_length=30,
        verbose_name="FIV",
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        default="NT",
    )
    felv = models.CharField(
        max_length=30,
        verbose_name="FELV",
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        default="NT",
    )
    primo_vaccine = models.CharField(
        max_length=3,
        verbose_name="Primo Vacciné(e)",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    vaccin_ok = models.CharField(
        max_length=3,
        verbose_name="Vaccins à jour",
        default="NON",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    type_vaccin = models.CharField(
        max_length=3,
        verbose_name="Type de vaccin",
        default="TC",
        choices=[(tag.name, tag.value) for tag in TypeVaccinChoice],
    )
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
        default="QUARANTAINE",
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
    ancien_proprio = models.ForeignKey(
        Person,
        verbose_name="Ancien propriétaire",
        related_name="anciens_animaux",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    inactif = models.BooleanField(
        default=False,
        verbose_name="Desactivé (Ne cocher que si vous ne souhaitez\
                                           plus gérer cet animal dans l'application) ",
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    contact = models.CharField(max_length=500, blank=True, verbose_name="Contact prise en charge")
    commentaire_sante = models.CharField(max_length=1000, blank=True)
    preference = models.OneToOneField(Preference, on_delete=models.PROTECT, blank=True, null=True)
    groupe = models.ForeignKey(AnimalGroup, on_delete=models.CASCADE, blank=True, null=True)
    commentaire_animaux_lies = models.CharField(max_length=1000, blank=True)
    nekosable = models.BooleanField(default=False, verbose_name="Nekosable")
    tranche_age = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Tranche d'âge",
        choices=[(tag.name, tag.value) for tag in TrancheAge],
    )
    perimetre = models.CharField(
        max_length=30,
        default="UN",
        verbose_name="Périmètre de gestion",
        choices=[(tag.name, tag.value) for tag in PerimetreChoice],
    )
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):

        # Déterminer la tranche d'age à partir de la date de naissance
        if self.date_naissance:
            today = timezone.now().date()
            twelve_months = today - timedelta(days=12 * 30)
            senior = today - timedelta(days=30 * 12 * 10)
            date_naissance = self.date_naissance
            if date_naissance > twelve_months:
                self.tranche_age = TrancheAge.ENFANT.name
            elif date_naissance > senior:
                self.tranche_age = TrancheAge.ADULTE.name
            else:
                self.tranche_age = TrancheAge.SENIOR.name
        # Mise à jour des préférences en fonction du statut
        if self.statut == StatutAnimal.QUARANTAINE.name:
            self.preference.quarantaine = OuiNonChoice.OUI.name
            self.preference.save()
        if self.statut == StatutAnimal.SOCIA.name:
            self.preference.sociabilisation = OuiNonChoice.OUI.name
            self.preference.save()
        if self.ancien_proprio:
            self.ancien_proprio.is_ancien_proprio = True
            self.ancien_proprio.save()
            # # Maj statut si adoption payée et retirer de la FA
        if (
            self.statut
            in (
                StatutAnimal.DECEDE.name,
                StatutAnimal.RENDU.name,
                StatutAnimal.PERDU.name,
                StatutAnimal.RELACHE.name,
            )
            and self.famille
        ):
            famille = self.famille
            for accueil in famille.accueil_set.filter(date_fin__isnull=True).filter(
                    animal__pk=self.id).all():
                accueil.date_fin = timezone.now().date()
                accueil.statut = StatutAccueil.TERMINE.name
                accueil.save()
            self.famille = None
            self.save()
        return super(Animal, self).save(*args, **kwargs)

    def get_latest_adoption(self):
        if self.adoption_set:
            return self.adoption_set.all().order_by("-id").first()
        return None

    def get_other_adoptions(self):
        if len(self.adoption_set.all()) > 1:
            return self.adoption_set.all().exclude(id=self.get_latest_adoption().id)
        return None

    def __str__(self):
        return self.nom

    def get_vaccin_str(self):
        #Primo vacciné
        date_str = ""
        if self.date_prochain_vaccin:
            date_str = " rappel avant le " + self.date_prochain_vaccin.strftime("%d/%m/%Y")
        if self.primo_vaccine == OuiNonChoice.OUI.name and self.vaccin_ok == OuiNonChoice.NON.name:
            return f"{self.type_vaccin}  Primo {date_str}"
        elif (
            self.primo_vaccine == OuiNonChoice.OUI.name and self.vaccin_ok == OuiNonChoice.OUI.name
        ):
            return self.type_vaccin + date_str
        else:
            return "Non"

    def get_tests_str(self):
        result = ""
        if self.fiv == TestResultChoice.POSITIVE.name:
            result += "FIV+ "
        if self.felv == TestResultChoice.POSITIVE.name:
            result += "FELV+"
        if self.fiv == TestResultChoice.NT.name or self.felv == TestResultChoice.NT.name:
            return "A faire"
        if self.fiv == TestResultChoice.NEGATIVE.name and self.felv == TestResultChoice.NEGATIVE.name:
            return "OK"
        return result

    def get_animaux_lies_str(self):
        result = ""
        if self.groupe:
            for animal in self.groupe.animal_set.all():
                if animal != self:
                    result += f"{animal.nom} "
        return result

    def get_animaux_lies(self):
        if self.groupe:
            return self.groupe.animal_set.exclude(id=self.pk)

    def is_sterilise(self):
        return self.sterilise == OuiNonChoice.OUI.name

    def is_en_soin_justif(self):
        return self.statut == StatutAnimal.SOIN.name and self.commentaire_sante

    def is_adoptable(self):
        return self.statut in [
            StatutAnimal.ADOPTABLE.name,
            StatutAnimal.A_ADOPTER.name,
        ]

    def get_montant_veto_total(self):
        montant_total = sum(
            vis.get_amount_per_animal()
            for vis in self.visites.all()
            if vis.get_amount_per_animal() != None
        )
        return f"{montant_total}"


class Parrainage(models.Model):
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    personne = models.ForeignKey(Person, on_delete=models.PROTECT)
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    type_paiement = models.CharField(
        max_length=20,
        verbose_name="Type de paiement",
        default=TypePaiementChoice.MENSUEL.name,
        choices=[(tag.name, tag.value) for tag in TypePaiementChoice],
    )
    montant = models.DecimalField(
        verbose_name="Montant du parrainage",
        max_digits=5,
        decimal_places=2, blank=True, null=True
    )
    date_nouvelles = models.DateField(verbose_name="Date des dernières nouvelles données", blank=True, null=True)

    class Meta:
        ordering = ['-date_debut']