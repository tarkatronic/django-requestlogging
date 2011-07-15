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
``logging_filters``
-------------------

Python uses `filters`_ to add contextural information to its
:mod:`~python:logging` facility.

Filters defined below are attached to :data:`settings.LOGGING` and
also :class:`~.middleware.LogSetupMiddleware`.

.. _filters:
   http://docs.python.org/2.6/library/logging.html#\
   adding-contextual-information-to-your-logging-output
"""


class RequestFilter(object):
    """
    Filter that adds information about a *request* to the logging record.

    :param request:
    :type request: :class:`~django.http.HttpRequest`

    Extra information can be substituted in the formatter string:

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
    """
    def __init__(self, request=None):
        """Saves *request* (a WSGIRequest object) for later."""
        self.request = request

    def filter(self, record):
        """
        Adds information from the request to the logging *record*.

        If certain information cannot be extracted from ``self.request``,
        a hyphen ``'-'`` is substituted as a placeholder.
        """
        request = self.request
        # Basic
        record.request_method = getattr(request, 'method', '-')
        record.path_info = getattr(request, 'path_info', '-')
        # User
        user = getattr(request, 'user', None)
        if user and not user.is_anonymous():
            record.username = user.username
        else:
            record.username = '-'
        # Headers
        META = getattr(request, 'META', {})
        record.remote_addr = META.get('REMOTE_ADDR', '-')
        record.server_protocol = META.get('SERVER_PROTOCOL', '-')
        record.http_user_agent = META.get('HTTP_USER_AGENT', '-')
        return True
