from django.db.models import BLANK_CHOICE_DASH
from django.forms import ModelForm, Form, CharField, ChoiceField, Select, IntegerField, DateField, DateInput, \
    ModelMultipleChoiceField, CheckboxSelectMultiple

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal
from gestion_association.models.famille import Famille, StatutFamille, Indisponibilite, Accueil
from gestion_association.widgets import TableSelectMultiple


class DateInput(DateInput):
    input_type = "date"


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
        fields = ("type_animal","commentaire","taille_logement","nb_places", "longue_duree", "statut","niveau")


class FamilleMainUpdateForm(ModelForm):
    class Meta:
        model = Famille
        fields = ("type_animal", "statut","niveau", "commentaire")


class FamilleAccueilUpdateForm(ModelForm):
    class Meta:
        model = Famille
        fields = ( "taille_logement","nb_places", "longue_duree")


class IndisponibiliteForm(ModelForm):
    class Meta:
        model = Indisponibilite
        fields = ("date_debut","date_fin")


class AccueilForm(ModelForm):
    class Meta:
        model = Accueil
        fields = ("date_debut","animaux","famille")

class SelectFamilleForm(ModelForm):

    class Meta:
        model = Accueil
        fields = ("date_debut","animaux","famille")

    animaux = ModelMultipleChoiceField(widget= CheckboxSelectMultiple, queryset = Animal.objects.none())
    famille = ModelMultipleChoiceField(queryset = Famille.objects.all(), required=False,
                                       widget=TableSelectMultiple(
                                           item_attrs=['get_nb_places_str', 'personne', 'get_disponibilite_str',
                                                       'get_preference_str', 'commentaire'],
                                           item_headers = ['Places disponibles', 'Personne', 'Disponibilité',
                                                           'Caractéristiques','Commentaire'],
                                           enable_datatables=True,
                                           bootstrap_style=True,
                                           datatable_options={'language': {'url': '/foobar.js'}},))
