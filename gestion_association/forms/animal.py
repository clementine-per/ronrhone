from dal import autocomplete

from django.db.models import BLANK_CHOICE_DASH
from django.forms import DateField, Form, CharField, ChoiceField, Select, ModelChoiceField, ModelForm, FileInput

class DateInput(DateInput):
    input_type = "date"

class TypeAnimalChoice(Enum):
    CHAT = "Chat"
    CHIEN = "Chien"
    LAPIN = "Lapin"

class AnimalSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    type_animal = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeAnimalChoice],
        widget=Select(),
        required=False,
    )
    date_naissance_min = DateField(
        label="Date de naissance entre le", required=False, widget=DateInput()
    )
    date_naissance_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_arrivee_min = DateField(
        label="Date de première arrivée entre le", required=False, widget=DateInput()
    )
    date_arrivee_max = DateField(
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
    date_adoption_min = DateField(
        label="Date d'adoption entre le", required=False, widget=DateInput()
    )
    date_adoption_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_caution_materiel_min = DateField(
        label="Date d'expiration de la caution materiel entre le", required=False, widget=DateInput()
    )
    date_caution_materiel_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )
    date_caution_sterilisation_min = DateField(
        label="Date d'expiration de la caution stérilisation entre le", required=False, widget=DateInput()
    )
    date_caution_sterilisation_max = DateField(
        label=" et le ", required=False, widget=DateInput()
    )