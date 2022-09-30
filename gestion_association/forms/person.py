from django.db.models import BLANK_CHOICE_DASH
from django.forms import CharField, ChoiceField, Form, ModelForm, Select, DateField

from gestion_association.forms import DateInput
from gestion_association.models.person import Person, TypePersonChoice, Adhesion


class PersonSearchForm(Form):
    nom = CharField(max_length=150, required=False)
    type_person = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypePersonChoice],
        widget=Select(),
        required=False,
        label="Rôle personne",
    )
    date_adhesion_min = DateField(
        label="Date de dernière adhésion entre le", required=False, widget=DateInput()
    )
    date_adhesion_max = DateField(label=" et le ", required=False, widget=DateInput())


class PersonForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Person
        fields = (
            "prenom",
            "nom",
            "email",
            "adresse",
            "code_postal",
            "ville",
            "telephone",
            "profession",
            "commentaire",
            "inactif",
        )

    def clean_ville(self):
        return self.cleaned_data['ville'].upper()

    def clean_nom(self):
        return self.cleaned_data['nom'].upper()


class BenevoleForm(ModelForm):
    class Meta:
        model = Person
        fields = ("commentaire_benevole",)


class AdhesionForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = Adhesion
        fields = ("date","montant","commentaire",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'


class ParrainageSearchForm(Form):
    nom_personne = CharField(max_length=150, required=False, label="Nom du parrain")
    nom_animal = CharField(max_length=150, required=False, label="Nom de l'animal")
    date_debut_min = DateField(
        label="Date de début du parrainage entre le", required=False, widget=DateInput()
    )
    date_debut_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_fin_min = DateField(
        label="Date de fin du parrainage entre le", required=False, widget=DateInput()
    )
    date_fin_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_nouvelles_min = DateField(
        label="Date des dernières nouvelles données entre le", required=False, widget=DateInput()
    )
    date_nouvelles_max = DateField(label=" et le ", required=False, widget=DateInput())

