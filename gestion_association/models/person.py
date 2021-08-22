from enum import Enum

from django.core.validators import RegexValidator
from django.db import models


# Enum utilisée pour l'écran de recherche
class TypePersonChoice(Enum):
    FA = "Famille d'accueil"
    ADOPTANTE = "Adoptante"
    BENEVOLE = "Bénévole"


class Person(models.Model):
    date_mise_a_jour = models.DateField(verbose_name="Date de mise à jour", auto_now=True)
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=150)
    nom_prenom_key = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=150)
    adresse = models.CharField(max_length=500)
    code_postal_regex = RegexValidator(
        regex="^[0-9]*$", message="Veuillez entrer un code postal valide."
    )
    code_postal = models.CharField(validators=[code_postal_regex], max_length=5)
    ville = models.CharField(max_length=100)
    telephone_regex = RegexValidator(
        regex="[0-9]{10}", message="Veuillez entrer un numéro de téléphone valide."
    )
    telephone = models.CharField(validators=[telephone_regex], max_length=10)
    date_inscription = models.DateField(auto_now_add=True)
    profession = models.CharField(max_length=250, blank=True)
    commentaire = models.CharField(max_length=1000, blank=True)
    inactif = models.BooleanField(
        default=False,
        verbose_name="Desactivé (Ne cocher que si vous ne souhaitez\
                                       plus gérer cette personne dans l'application) ",
    )
    is_famille = models.BooleanField(default=False, verbose_name="Famille d'accueil")
    is_adoptante = models.BooleanField(default=False, verbose_name="Adoptante")
    is_benevole = models.BooleanField(default=False, verbose_name="Bénévole")
    commentaire_benevole = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="Information sur le rôle de cette bénévole au sein de l'association",
    )

    def get_adresse_complete(self):
        return f"{self.adresse} \n {self.code_postal} {self.ville}"

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def has_role(self):
        return self.is_famille or self.is_benevole or self.is_adoptante
