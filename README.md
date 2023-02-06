# Application de gestion Ronrhone

Bienvenue sur le projet de gestion de l'association de protection animale Ronrhône

## Installation

Créez un environnement virtuel Python

```bash
virtualenv venv
```

Activez l'environnement avec

```bash
#For Windows
source ./ven/Scripts/activate

#For Linux
source ./ven/bin/activate
```

Installez les dépendances

```bash
pip install -r requirements.txt
```

## Pour lancer le projet

Activez l'environnement avec

```bash
#For Windows
source ./ven/Scripts/activate

#For Linux
source ./ven/bin/activate
```

Indiquez qu'il s'agit de l'environnement local

```bash
export DJANGO_SETTINGS_MODULE=ronrhone.local_settings
```

Mettez à la jour la base de données

```bash
python manage.py migrate --run-syncdb
```

Créez un administrateur

```bash
python manage.py createsuperuser
```

Lancez le serveur

```bash
python manage.py runserver localhost:8000
```

Enjoy! <http://localhost:8000/ronrhone/>

## pre-commit hooks

pre-commit is a tool that will run a list of checks on the files you are trying to commit.

Make sure to provide the `pre-commit` command on your shell path.

You can install it from here: <https://pre-commit.com/>

### Install pre-commit hook for ronrhone

```bash
pre-commit install
```

### Will it slow me down?

The benefit of `pre-commit` is that it only checks the file you changed so it is rather quick and we don't need to exclude files that are not committed.

### Can I run it to check all existing files?

If you are adding a new check, you might want to run it on the whole code base.

To do so, you can run:

```bash
pre-commit run --all-files
```

If you do so, make sure to commit your local changes before running
the command because you might want to erase what it did.

```bash
# make local changes
git commit -am "My changes"

# Run pre-commit
pre-commit run --all-files

# discover that it does do what you wanted
git reset HEAD --hard

# change your hooks configuration
pre-commit run --all-files
...
```
