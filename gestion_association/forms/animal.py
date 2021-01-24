from enum import Enum

from dal import autocomplete
from django.conf import settings

from django.db.models import BLANK_CHOICE_DASH
from django.forms import DateField, Form, CharField, ChoiceField, Select, ModelChoiceField, ModelForm, FileInput, \
    DateInput, BooleanField, MultipleChoiceField, Widget, TextInput
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget, Select2MultipleWidget, \
    HeavySelect2MultipleWidget

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import TypeChoice, StatutAnimal, Animal, Preference


class DateInput(DateInput):
    input_type = "date"


class AnimalSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    identification = CharField(max_length=100, required=False, label="Numéro d'identification")
    type = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeChoice],
        widget=Select(),
        required=False,
    )
    sterilise = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    date_naissance_min = DateField(
        label="Date de naissance entre le", required=False, widget=DateInput()
    )
    date_naissance_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_vermifuge_min = DateField(
        label="Date du dernier vermifuge entre le", required=False, widget=DateInput()
    )
    date_vermifuge_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_prochaine_visite_min = DateField(
        label="Date de prochaine visite vétérinaire entre le",
        required=False,
        widget=DateInput(),
    )
    date_prochaine_visite_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    sans_fa = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    statuts = MultipleChoiceField(
        choices=[(tag.name, tag.value) for tag in StatutAnimal],
        required=False,
        initial=[tag.name for tag in StatutAnimal]
    )


class AnimalCreateForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("nom","sexe","type","date_naissance","identification","circonstances", "date_arrivee"
                  , "commentaire","statut","sterilise","date_sterilisation","vaccine",
                  "date_dernier_vaccin", "date_prochain_vaccin", "fiv","felv", "date_parasite")


class AnimalInfoUpdateForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("nom","sexe","type","date_naissance","identification","circonstances", "date_arrivee"
                  , "commentaire","statut")



class AnimalSanteUpdateForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("sterilise","date_sterilisation","vaccine",
                  "date_dernier_vaccin", "date_prochain_vaccin", "fiv","felv", "date_parasite")
