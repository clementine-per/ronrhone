from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, CharField, ModelForm, ChoiceField, Select

from gestion_association.models.person import Person, TypePersonChoice


class PersonSearchForm(Form):
    nom = CharField(max_length=150, required=False)
    type_person = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypePersonChoice],
        widget=Select(),
        required=False,
    )

class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ("nom","prenom","email","adresse","code_postal","ville", "telephone"
                  , "profession","commentaire")