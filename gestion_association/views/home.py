from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def index(request):
    selected = "accueil"
    return render(request, "gestion_association/home.html", locals())