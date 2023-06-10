from django.urls import path

from monday_api.views import check_api_fa, index, integrate_fa

urlpatterns = [
    path("", index, name="monday"),
    path("fa-check", check_api_fa, name="check_api_fa"),
    path("fa-import", integrate_fa, name="integrate_fa"),
]