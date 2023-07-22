from django.urls import path

from monday_api.views import index
from monday_api.views.adoption import check_api_adoptions, integrate_adoptions
from monday_api.views.family import check_api_fa, integrate_fa

urlpatterns = [
    path("", index, name="monday"),
    path("fa-check", check_api_fa, name="check_api_fa"),
    path("fa-import", integrate_fa, name="integrate_fa"),
    path("adoptions-check", check_api_adoptions, name="check_api_adoptions"),
    path("adoptions-import", integrate_adoptions, name="integrate_adoptions"),
]