from django.forms import ModelForm

from gestion_association.models.animal import Preference


class PreferenceForm(ModelForm):
    class Meta:
        model = Preference
        fields = "__all__"
