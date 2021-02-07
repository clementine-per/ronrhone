import sys
from enum import Enum

from django.db import models

from gestion_association.models import OuiNonChoice
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
    date_mise_a_jour = models.DateField(
        verbose_name="Date de mise à jour", auto_now=True
    )
    personne = models.ForeignKey(
        Person,
        verbose_name="Personne",
        on_delete=models.PROTECT,
    )
    statut = models.CharField(max_length=20, blank=True,
                                verbose_name="Statut",
                                choices=[(tag.name, tag.value) for tag in StatutFamille])
    niveau = models.CharField(max_length=20, blank=True,
                              verbose_name="Niveau",
                              choices=[(tag.name, tag.value) for tag in Niveau])
    nb_animaux_historique = models.IntegerField(
        null=True, verbose_name="Nombre d'animaux au total"
    )
    commentaire = models.CharField(max_length=1000, blank=True)
    taille_logement = models.IntegerField(
        null=True, verbose_name="Taille du logement (en mètres carrés)")
    longue_duree = models.CharField(max_length=3, default="OUI",
                                   verbose_name="Accepte les acceuils de longue durée",
                                   choices=[(tag.name, tag.value) for tag in OuiNonChoice])
    nb_places = models.IntegerField(verbose_name="Nombre de places")
    preference = models.OneToOneField('Preference', on_delete=models.PROTECT, blank=True, null=True)

    def get_nb_places_str(self):
        count = self.nb_places
        if (self.animal_set):
            count -= self.animal_set.count();
        return str(count) + "/" + str(self.nb_places)

    def get_indisponibilites_str(self):
        result = ""
        print(self.indisponibilite_set.all())
        sys.stdout.flush()
        if (self.indisponibilite_set.all()):
            for indispo in self.indisponibilite_set:
                result += "Du "
                result += indispo.date_debut
                result += " au "
                result += indispo.date_fin
                result += "<br>"
        return result




class Indisponibilite(models.Model):
    date_debut = models.DateField(verbose_name="Date de départ")
    date_fin = models.DateField(verbose_name="Date de retour")
    famille = models.ForeignKey(Famille, on_delete=models.PROTECT)