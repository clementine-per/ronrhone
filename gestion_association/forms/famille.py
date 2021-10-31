from django.core.exceptions import ValidationError
from django.db.models import BLANK_CHOICE_DASH
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    DateField,
    DateInput,
    Form,
    IntegerField,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    Select,
)
from django.utils import timezone

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal
from gestion_association.models.famille import Accueil, Famille, Indisponibilite, StatutFamille


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
    vide = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    date_presence_min = DateField(label="Plage recherchée du", required=False, widget=DateInput())
    date_presence_max = DateField(label=" au ", required=False, widget=DateInput())


class FamilleCreateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Famille
        fields = (
            "type_animal",
            "commentaire",
            "taille_logement",
            "autres_animaux",
            "nb_places",
            "detail_places",
            "longue_duree",
            "statut",
            "niveau",
            "nb_heures_absence"
        )


class FamilleMainUpdateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Famille
        fields = ("type_animal", "statut", "niveau", "commentaire")


class FamilleAccueilUpdateForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Famille
        fields = ("taille_logement", "autres_animaux", "nb_places", "detail_places", "longue_duree","nb_heures_absence")


class IndisponibiliteForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Indisponibilite
        fields = ("date_debut", "date_fin")

    def __init__(self, *args, **kwargs):
        super(IndisponibiliteForm, self).__init__(*args, **kwargs)
        self.fields['date_debut'].widget.attrs['class'] = 'datePicker'
        self.fields['date_fin'].widget.attrs['class'] = 'datePicker'

    def clean_date_fin(self):
        date_fin = self.cleaned_data['date_fin']
        date_debut = self.cleaned_data['date_debut']
        if not date_fin > date_debut:
            raise ValidationError("La date de fin ne peut se trouver avant la date de début.")
        return date_fin


class AccueilForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Accueil
        fields = ("date_debut","date_fin","commentaire")

    def __init__(self, *args, **kwargs):
        super(AccueilForm, self).__init__(*args, **kwargs)
        self.fields['date_debut'].widget.attrs['class'] = 'datePicker'
        self.fields['date_fin'].widget.attrs['class'] = 'datePicker'


class SelectFamilleForm(Form):

    date_debut = DateField(label="Date de début")
    animaux = ModelMultipleChoiceField(
        widget=CheckboxSelectMultiple, queryset=Animal.objects.none()
    )
    famille = ModelChoiceField(queryset=Famille.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_debut'].widget.attrs['class'] = 'datePicker'
