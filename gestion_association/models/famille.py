from enum import Enum

from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from gestion_association.models import OuiNonChoice, TypeChoice
from gestion_association.models.person import Person


class StatutFamille(Enum):
    DISPONIBLE = "Disponible"
    INDISPONIBLE = "Temporairement indisponible"
    INACTIVE = "Inactive"


class Niveau(Enum):
    DEBUTANT = "Débutant"
    INTERMEDIAIRE = "Intermédiaire"
    CONFIRME = "Confirmé"


class Famille(models.Model):
    date_mise_a_jour = models.DateField(verbose_name="Date de mise à jour", auto_now=True)
    personne = models.OneToOneField(
        Person,
        verbose_name="Personne",
        on_delete=models.PROTECT,
    )
    statut = models.CharField(
        max_length=20,
        verbose_name="Statut",
        default="DISPONIBLE",
        choices=[(tag.name, tag.value) for tag in StatutFamille],
    )
    niveau = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Niveau",
        default="DEBUTANT",
        choices=[(tag.name, tag.value) for tag in Niveau],
    )
    nb_animaux_historique = models.IntegerField(
        default=0, verbose_name="Nombre d'animaux au total"
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    taille_logement = models.IntegerField(
        null=True, verbose_name="Taille du logement (en mètres carrés)"
    )
    longue_duree = models.CharField(
        max_length=3,
        default="OUI",
        verbose_name="Accepte les acceuils de longue durée",
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
    )
    nb_places = models.IntegerField(verbose_name="Nombre de places")
    preference = models.OneToOneField(
        "Preference", on_delete=models.PROTECT, blank=True, null=True
    )
    type_animal = models.CharField(
        max_length=30,
        verbose_name="Type d'animal accueilli",
        default="CHAT",
        choices=[(tag.name, tag.value) for tag in TypeChoice],
    )

    def get_nb_places_str(self):
        count = self.nb_places
        if self.animal_set:
            count -= self.animal_set.count()
        return str(count) + "/" + str(self.nb_places)

    def get_indisponibilites_str(self):
        result = ""
        if self.indisponibilite_set.order_by("date_debut").all():
            for indispo in self.indisponibilite_set.all():
                result += str(indispo)
                result += "<br>"
        return mark_safe(result)

    def get_disponibilite_str(self):
        today = timezone.now().date()
        result = self.get_statut_display()
        prochaines_indispos = self.indisponibilite_set.filter(date_fin__gte=today).all()
        if prochaines_indispos:
            result += "\n"
            result += "Prochaines indisponibilités : "
            for indispo in prochaines_indispos:
                result += "\n"
                result += str(indispo)
        return mark_safe(result)

    def get_preference_str(self):
        result = ""
        result += "Famille pour "
        result += self.get_type_animal_display()
        result += " de niveau "
        result += self.get_niveau_display()
        result += "\n"
        if self.taille_logement:
            result += "Logement de "
            result += str(self.taille_logement)
            result += " m2"
        if self.preference.exterieur and self.preference.exterieur == "OUI":
            result += " avec extérieur"
        else:
            result += " sans extérieur"
        result += "\n"
        if self.longue_duree and self.longue_duree == "OUI":
            result += "OK longues durées"
            result += "\n"
        if self.preference.sociabilisation and self.preference.sociabilisation == "OUI":
            result += "OK sociabilisation"
            result += "\n"
        if self.preference.quarantaine and self.preference.quarantaine == "OUI":
            result += "OK quarantaine"
            result += "\n"
        if self.preference.biberonnage and self.preference.biberonnage == "OUI":
            result += "OK biberonnage"
            result += "\n"
        result += "Niveau de présence : "
        result += self.preference.get_presence_display()
        result += "\n"
        return result

    def to_json(self):
        return {
            "id": self.pk,
            "places_disponible": self.get_nb_places_str(),
            "personne": str(self.personne),
            "disponibilites": self.get_disponibilite_str(),
            "caracteristiques": self.get_preference_str(),
            "commentaire": self.commentaire,
        }


class Indisponibilite(models.Model):
    date_debut = models.DateField(verbose_name="Date de départ")
    date_fin = models.DateField(verbose_name="Date de retour")
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT)

    def __str__(self):
        result = "Du "
        result += self.date_debut.strftime("%d/%m/%Y")
        result += " au "
        result += self.date_fin.strftime("%d/%m/%Y")
        return result


class Accueil(models.Model):
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT)
    animaux = models.ManyToManyField("Animal", verbose_name="Animal(aux)")
    commentaire = models.CharField(max_length=1000, blank=True)
