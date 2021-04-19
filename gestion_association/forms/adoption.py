from django.db.models import BLANK_CHOICE_DASH
from django.forms import ChoiceField, Form, ModelForm, Select, IntegerField, CharField, DateField, DateInput

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption, BonSterilisation
from gestion_association.models.animal import Animal, StatutAnimal


class AdoptionCreateFormNoAdoptant(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class AdoptionSearchForm(Form):
    montant_restant = IntegerField(required=False, label="Montant restant minimum")
    animal = CharField(max_length=150)
    pre_visite = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    visite_controle = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    date_min = DateField(
        label="Date d'adoption entre le", required=False, widget=DateInput()
    )
    date_max = DateField(
        label="et le", required=False, widget=DateInput()
    )


class AdoptionCreateForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "adoptant",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class AdoptionFromUserForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "animal",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animal"].queryset = Animal.objects.filter(statut=StatutAnimal.A_ADOPTER.name)


class AdoptionUpdateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class ShowBonForm(Form):
    # Champ indiquant si on doit afficher le formulaire de bon de stérilisation
    show = ChoiceField(
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        label="Bon de stérilisation",
    )


class BonSterilisationForm(ModelForm):
    class Meta:
        model = BonSterilisation
        fields = ("date_max", "envoye", "utilise", "date_utilisation")
