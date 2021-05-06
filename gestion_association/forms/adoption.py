from django.db.models import BLANK_CHOICE_DASH
from django.forms import ChoiceField, Form, ModelForm, Select, IntegerField, CharField, DateField, DateInput, \
    MultipleChoiceField, SelectMultiple

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption, BonSterilisation, OuiNonVisiteChoice
from gestion_association.models.animal import Animal, StatutAnimal
from gestion_association.models.person import Person


class DateInput(DateInput):
    input_type = "date"

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["personne_visite"].queryset = Person.objects.filter(is_benevole=True).order_by('nom')


class AdoptionSearchForm(Form):
    montant_restant = IntegerField(required=False, label="Montant restant minimum")
    animal = CharField(required=False, max_length=150)
    pre_visite = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    visite_controle = MultipleChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonVisiteChoice],
        required=False,
        initial=[tag.name for tag in OuiNonVisiteChoice],
        widget=SelectMultiple(attrs={'class': "selectpicker"})
    )

    date_min = DateField(
        label="Date d'adoption entre le", required=False, widget=DateInput()
    )
    date_max = DateField(
        label="et le", required=False, widget=DateInput()
    )
    statut = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in StatutAnimal],
        required=False,
        widget=Select()
    )
    date_expiration_min = DateField(
        label="Date d'expiration entre le", required=False, widget=DateInput()
    )
    date_expiration_max = DateField(
        label="et le", required=False, widget=DateInput()
    )
    bon_envoye = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    bon_utilise = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["personne_visite"].queryset = Person.objects.filter(is_benevole=True).order_by('nom')


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
        self.fields["personne_visite"].queryset = Person.objects.filter(is_benevole=True).order_by('nom')


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["personne_visite"].queryset = Person.objects.filter(is_benevole=True).order_by('nom')


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
