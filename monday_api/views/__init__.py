from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from gestion_association.views.utils import admin_test


@user_passes_test(admin_test)
def index(request):
    selected = "monday"
    title = "Intégration avec Monday"
    return render(request, "monday_api/index.html", locals())