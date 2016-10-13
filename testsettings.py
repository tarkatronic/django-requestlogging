INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_requestlogging',
)

SECRET_KEY = 'foobar'

MIDDLEWARE_CLASSES = (
    'django_requestlogging.middleware.LogSetupMiddleware'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}
