from django.forms import ModelForm, DateInput

from gestion_association.models.animal import Preference


class DateInput(DateInput):
    input_type = "date"


class PreferenceForm(ModelForm):
    class Meta:
        model = Preference
        fields = "__all__"
