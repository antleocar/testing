"""
Django settings for fsworld project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from urlparse import urlparse
import os
from django.conf import global_settings
from django.contrib.messages import constants as message_constants
from django.core.urlresolvers import reverse


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if os.getenv('DEBUG', "True") == "True":
    DEBUG = True
else:
    DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

MONGO_DEFAULT = 'mongodb://127.0.0.1/fsworld'
MONGO_URL = urlparse(os.getenv('MONGOHQ_URL', MONGO_DEFAULT))
MONGO_DB = MONGO_URL.path[1:]
MONGO_HOST = MONGO_URL.hostname
MONGO_PORT = MONGO_URL.port
MONGO_USER = MONGO_URL.username
MONGO_PASS = MONGO_URL.password


DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_engine',
        'NAME': MONGO_DB,
        'USER': MONGO_USER,
        'PASSWORD': MONGO_PASS,
        'HOST': MONGO_HOST,
        'PORT': MONGO_PORT,
        'SUPPORTS_TRANSACTIONS': False,
    }
}


ALLOWED_HOSTS = ['*']


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

TIME_ZONE = 'Europe/Madrid'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7bmvys@hkimq!7y=s0%v(p2=0x=kp3a27j**^44*tmscnhc1%0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'fsworld.urls'

WSGI_APPLICATION = 'fsworld.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(BASE_DIR, '..', 'templates').replace('\\','/')
    os.path.join(BASE_DIR, 'templates').replace('\\', '/'),

)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fsworld',
    'webapp',
    'djangotoolbox',
    'rest_framework',
    'sorl.thumbnail',
    

)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    # Anadido para la navegabilidad, de este modo se activa la etiqueta 'active' cuando navegamos.
    'django.core.context_processors.request',
    # Login social
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


LOGIN_REDIRECT_URL = reverse('main')
LOGIN_URL = reverse('login')

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

#Configuration for django.core.mail.sendmail
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL', "")
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASSWORD', "")
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = 'fs-world: '
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv('DJANGO_EMAIL', "")


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

    'DATETIME_FORMAT': ['%s']
}








