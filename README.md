# Application de gestion Ronrhone

Bienvenue sur le projet de gestion de l'association de protection animale Ronrhône

## Installation

Créez un environnement virtuel Python

    virtualenv ronrhone

Activez l'environnement avec

    source ./ronrhone/Scripts/activate

Installez les dépendances

	pip install -r requirements.txt

## Pour lancer le projet

Activez l'environnement avec

	source ./ronrhone/Scripts/activate

Mettez à la jour la base de données

    ./manage.py migrate

Créez un administrateur

	./manage.py createsuperuser

Lancez le serveur

	./manage.py runserver

Enjoy! http://localhost:8000/ronrhone/