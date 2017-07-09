INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_requestlogging',
    'testapp',
)

SECRET_KEY = 'foobar'

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    'django_requestlogging.middleware.LogSetupMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

ROOT_URLCONF = 'testapp.urls'
