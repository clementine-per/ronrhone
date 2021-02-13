from django.db.models import BLANK_CHOICE_DASH
from django.forms import ModelForm, Form, CharField, ChoiceField, Select, IntegerField, DateField, DateInput

from gestion_association.models import OuiNonChoice
from gestion_association.models.famille import Famille, StatutFamille


class FamilleSearchForm(Form):
    nom_personne = CharField(max_length=100, required=False, label="Nom de la personne")
    statut = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in StatutFamille],
        widget=Select(),
        required=False,
    )
    places_dispos = IntegerField(required=False, label="Nombre de places disponibles minimum")
    quarantaine = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    exterieur = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    date_presence_min = DateField(
        label="Plage recherchée du", required=False, widget=DateInput()
    )
    date_presence_max = DateField(
        label=" au ", required=False, widget=DateInput()
    )


class FamilleCreateForm(ModelForm):
    class Meta:
        model = Famille
        fields = ("commentaire","taille_logement","nb_places", "longue_duree")
