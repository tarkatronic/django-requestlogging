# -*- mode: django; coding: utf-8 -*-
#
# Copyright © 2011, TrustCentric
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of TrustCentric nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Request logging middleware
``````````````````````````
"""


import logging
import weakref

import six
from django_requestlogging.logging_filters import RequestFilter


weakref_type = type(weakref.ref(lambda: None))


def deref(x):
    return x() if x and type(x) == weakref_type else x


class LogSetupMiddleware(object):
    """
    Adds :class:`.logging_filters.RequestFilter` to every request.

    If *root* is a module name, only look at loggers inside that
    logging subtree.

    This filter adds useful information about `HttpRequest`\ s to log
    entries. See :class:`.logging_filters.RequestFilter` for details
    about which formatter substitutions are added.

    Automatically detects which handlers and logger need
    RequestFilter installed, by looking for an unbound RequestFilter
    attached to a handler or logger. To configure Django, in your
    :envvar:`DJANGO_SETTINGS_MODULE`::

       LOGGING = {
           'filters': {
               # Add an unbound RequestFilter.
               'request': {
                   '()': 'django_requestlogging.logging_filters.RequestFilter',
               },
           },
           'handlers': {
               'console': {
                   'class': 'logging.StreamHandler',
                   'filters': ['request'],
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
    """
    FILTER = RequestFilter

    def __init__(self, root=''):
        self.root = root

    def find_loggers(self):
        """
        Returns a :class:`dict` of names and the associated loggers.
        """
        # Extract the full logger tree from Logger.manager.loggerDict
        # that are under ``self.root``.
        result = {}
        prefix = self.root + '.'
        for name, logger in six.iteritems(logging.Logger.manager.loggerDict):
            if self.root and not name.startswith(prefix):
                # Does not fall under self.root
                continue
            result[name] = logger
        # Add the self.root logger
        result[self.root] = logging.getLogger(self.root)
        return result

    def find_handlers(self):
        """
        Returns a list of handlers.
        """
        return list(logging._handlerList)

    def _find_filterer_with_filter(self, filterers, filter_cls):
        """
        Returns a :class:`dict` of filterers mapped to a list of filters.

        *filterers* should be a list of filterers.

        *filter_cls* should be a logging filter that should be matched.
        """
        result = {}
        for logger in map(deref, filterers):
            filters = [f for f in map(deref, getattr(logger, 'filters', []))
                       if isinstance(f, filter_cls)]
            if filters:
                result[logger] = filters
        return result

    def find_loggers_with_filter(self, filter_cls):
        """
        Returns a :class:`dict` of loggers mapped to a list of filters.

        Looks for instances of *filter_cls* attached to each logger.
        If the logger has at least one, it is included in the result.
        """
        return self._find_filterer_with_filter(self.find_loggers().values(),
                                               filter_cls)

    def find_handlers_with_filter(self, filter_cls):
        """
        Returns a :class:`dict` of handlers mapped to a list of filters.

        Looks for instances of *filter_cls* attached to each handler.
        If the handler has at least one, it is included in the result.
        """
        return self._find_filterer_with_filter(self.find_handlers(),
                                               filter_cls)

    def add_filter(self, f, filter_cls=None):
        """Add filter *f* to any loggers that have *filter_cls* filters."""
        if filter_cls is None:
            filter_cls = type(f)
        for logger in self.find_loggers_with_filter(filter_cls):
            logger.addFilter(f)
        for handler in self.find_handlers_with_filter(filter_cls):
            handler.addFilter(f)

    def remove_filter(self, f):
        """Remove filter *f* from all loggers."""
        for logger in self.find_loggers_with_filter(type(f)):
            logger.removeFilter(f)
        for handler in self.find_handlers_with_filter(type(f)):
            handler.removeFilter(f)

    def process_request(self, request):
        """Adds a filter, bound to *request*, to the appropriate loggers."""
        request.logging_filter = RequestFilter(request)
        self.add_filter(request.logging_filter)

    def process_response(self, request, response):
        """Removes this *request*'s filter from all loggers."""
        f = getattr(request, 'logging_filter', None)
        if f:
            self.remove_filter(f)
        return response

    def process_exception(self, request, exception):
        """Removes this *request*'s filter from all loggers."""
        f = getattr(request, 'logging_filter', None)
        if f:
            self.remove_filter(f)
