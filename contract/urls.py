from django.urls import path

from contract.views import generate_contract

urlpatterns = [
    # Génération contrat
    path("<int:pk>/", generate_contract, name="generer_contrat")
]