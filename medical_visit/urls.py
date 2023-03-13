from django.urls import path

from medical_visit.views import *

urlpatterns = [
    # Medical visits
    path(
        "list/",
        visite_medicale_list,
        name="visites",
    ),
    path("create/", create_visite_medicale, name="create_visite"),
    path("update/<int:pk>/", UpdateVisiteMedicale.as_view(), name="update_visite"),
    path("create_animal/<int:pk>/", create_visite_from_animal, name="create_visite_animal"),
    path(
        "delete/<int:pk>/",
        delete_visite,
        name="delete_visite",
    ),
]