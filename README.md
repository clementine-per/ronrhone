# Ronrhone management application

Welcome to the management project of the Ronrhône animal protection association.

## Installation

Create a new virtual environment

```bash
virtualenv venv
```

Activate the virtual environment

```bash
#For Windows
source ./venv/Scripts/activate

#For Linux
source ./venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## To run the project locally

Activate the virtual environment

```bash
#For Windows
source ./venv/Scripts/activate

#For Linux
source ./venv/bin/activate
```

Use local settings for development

```bash
export DJANGO_SETTINGS_MODULE=ronrhone.local_settings
```

Update the database

```bash
python manage.py migrate --run-syncdb
```

Create the superuser

```bash
python manage.py createsuperuser
```

Run the server

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
