# Prod
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['ronrhone.pythonanywhere.com']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'ronrhone$default',
        "USER": 'ronrhone',
        "PASSWORD": [PASSWORD],
        'HOST': 'ronrhone.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join("/home/ronrhone/ronrhone/static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'gestion_association/static'),
    os.path.join(BASE_DIR, 'static')
]