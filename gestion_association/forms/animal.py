import json
from string import capwords

from django.db.models import BLANK_CHOICE_DASH
from django.forms import DateField, Form, CharField, ChoiceField, Select, ModelChoiceField, ModelForm, FileInput, \
    DateInput, BooleanField, MultipleChoiceField, Widget, TextInput
from django.forms import CheckboxInput, SelectMultiple, ModelMultipleChoiceField
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe


from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import TypeChoice, StatutAnimal, Animal, Preference
from gestion_association.models.famille import Famille
from gestion_association.widgets import TableSelectMultiple


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

class AnimalLinkedForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("animaux_lies",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animaux_lies"].queryset = Animal.objects.filter(statut__in=[StatutAnimal.A_ADOPTER.name,
                                                                     StatutAnimal.QUARANTAINE.name,
                                                                     StatutAnimal.SEVRAGE.name, StatutAnimal.SOCIA.name,
                                                                     StatutAnimal.SOIN.name])


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


class SelectFamilleForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("famille",)

    famille = ModelMultipleChoiceField( queryset = Famille.objects.all(), required=False,
                                             widget=TableSelectMultiple(
        item_attrs=['date_mise_a_jour', 'personne', 'statut'],
       enable_datatables=True,
       bootstrap_style=True,
       datatable_options={'language': {'url': '/foobar.js'}},))