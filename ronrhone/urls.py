"""ronrhone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from gestion_association.views.animal import AnimalViewSet

router = routers.DefaultRouter()
router.register(r'animals', AnimalViewSet)

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accueil")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/ronRhonE1901", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path("ronrhone/", include("gestion_association.urls")),
    path("ronrhone/contract/", include("contract.urls")),
]
