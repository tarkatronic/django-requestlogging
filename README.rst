django-requestlogging
=====================

.. image:: https://travis-ci.org/tarkatronic/django-requestlogging.svg?branch=master
    :target: https://travis-ci.org/tarkatronic/django-requestlogging

This package provides a logging filter and middleware to add
information about the current request to the logging record.


Installation and Usage
----------------------

Install the package, add ``django_requestlogging`` to
``settings.INSTALLED_APPS``, add
``django_requestlogging.middleware.LogSetupMiddleware`` to
``settings.MIDDLEWARE_CLASSES``, and add
``django_requestlogging.logging_filters.RequestFilter`` as a logging
filter.  See below for an example logging configuration.

The filter adds information about the current request to the logging
record.  The following keys can be substituted in the logging
formatter string:

    ``http_user_agent``
       The user agent string, provided by the client.

    ``path_info``
       The requested HTTP path.

    ``remote_addr``
       The remote IP address.

    ``request_method``
       The HTTP request method (*e.g.* GET, POST, PUT, DELETE, *etc.*)

    ``server_protocol``
       The server protocol (*e.g.* HTTP, HTTPS, *etc.*)

    ``username``
       The username for the logged-in user.

If any of this information cannot be extracted from the current
request (or there is no current request), a hyphen ``'-'`` is
substituted as a placeholder.


Logging Configuration Example
-----------------------------

This logging configuration can be added to your
``DJANGO_SETTINGS_MODULE``.  It adds an unbound RequestFilter,
which will be bound to the current request by the middleware and then
unbound again at response time.
::

  LOGGING = {
      'filters': {
          # Add an unbound RequestFilter.
          'request': {
              '()': 'django_requestlogging.logging_filters.RequestFilter',
          },
      },
      'formatters': {
          'request_format': {
              'format': '%(remote_addr)s %(username)s "%(request_method)s '
              '%(path_info)s %(server_protocol)s" %(http_user_agent)s '
              '%(message)s %(asctime)s',
          },
      },
      'handlers': {
          'console': {
              'class': 'logging.StreamHandler',
              'filters': ['request'],
              'formatter': 'request_format',
          },
      },
      'loggers': {
          'myapp': {
              # Add your handlers that have the unbound request filter
              'handlers': ['console'],
              # Optionally, add the unbound request filter to your
              # application.
              'filters': ['request'],
          },
      },
  }

