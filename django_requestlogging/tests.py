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

try:
    reload  # Python 2.7
except NameError:
    from importlib import reload  # Python 3.4+
import logging

import six
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from django_requestlogging.logging_filters import RequestFilter
from django_requestlogging.middleware import LogSetupMiddleware, deref


class LogSetupMiddlewareTest(TestCase):
    maxDiff = None

    def setUp(self, *args, **kwargs):
        super(LogSetupMiddlewareTest, self).setUp(*args, **kwargs)
        self.factory = RequestFactory()
        # LogSetupMiddleware only looks under this module
        logging_root = __name__
        self.middleware = LogSetupMiddleware(root=logging_root)
        self.filter = RequestFilter(request=None)
        # Create test logger with a placeholder logger
        self.logger = logging.getLogger(__name__)
        self.logger.filters = []
        self.logger.addFilter(self.filter)
        # Stub out original handlers
        self._original_handlers = logging._handlers
        self._original_handlerList = logging._handlerList
        logging._handlers = {}
        logging._handlerList = []
        # Create test handler
        self.handler = logging.NullHandler()
        self.handler.filters = []
        self.handler.addFilter(self.filter)
        self.logger.addHandler(self.handler)

    def tearDown(self, *args, **kwargs):
        logging._handlers = self._original_handlers
        logging._handlerList = self._original_handlerList

    def bound_logger(self, request):
        loggers = self.middleware.find_loggers_with_filter(RequestFilter)
        for logger, filters in six.viewitems(loggers):
            if any(f.request == request for f in filters):
                return True
        return False

    def bound_handler(self, request):
        handlers = self.middleware.find_handlers_with_filter(RequestFilter)
        for handler, filters in six.viewitems(handlers):
            if any(f.request == request for f in filters):
                return True
        return False

    def assertBound(self, request):
        self.assertTrue(self.bound_logger(request))
        self.assertTrue(self.bound_handler(request))

    def assertNotBound(self, request):
        self.assertFalse(self.bound_logger(request))
        self.assertFalse(self.bound_handler(request))

    def test_request(self):
        request = self.factory.get('/')
        self.assertNotBound(request)
        response = self.middleware.process_request(request)
        self.assertBound(request)
        self.middleware.process_response(request, response)

    def test_response(self):
        request = self.factory.get('/')
        self.assertNotBound(request)
        response = self.middleware.process_request(request)
        self.assertBound(request)
        self.middleware.process_response(request, response)
        self.assertNotBound(request)

    def test_exception(self):
        request = self.factory.get('/')
        self.assertNotBound(request)
        self.middleware.process_request(request)
        self.assertBound(request)
        self.middleware.process_exception(request, Exception())
        self.assertNotBound(request)

    def test_process_response_alone(self):
        request = self.factory.get('/')
        self.assertNotBound(request)
        self.middleware.process_response(request, HttpResponse(''))
        self.assertNotBound(request)

    def test_process_exception_alone(self):
        request = self.factory.get('/')
        self.assertNotBound(request)
        self.middleware.process_exception(request, Exception())
        self.assertNotBound(request)

    def test_find_loggers(self):
        # Find a subset of loggers
        self.assertEqual(self.middleware.find_loggers(),
                         {__name__: self.logger})
        # Look for all loggers
        self.middleware.root = ''
        loggers = self.middleware.find_loggers()
        self.assertEqual(loggers[''], logging.getLogger(''))
        self.assertEqual(loggers[__name__], self.logger)

    def test_find_loggers_with_filter(self):
        loggers = self.middleware.find_loggers_with_filter(RequestFilter)
        self.assertListEqual(list(six.viewkeys(loggers)), [self.logger])
        self.assertEqual([type(f) for f in loggers[self.logger]],
                         [RequestFilter],
                         loggers[self.logger])

    def test_find_handlers(self):
        # Find our handler
        self.assertTrue(self.handler in map(deref, self.middleware.find_handlers()))

    def test_find_handlers_with_filter(self):
        handlers = self.middleware.find_handlers_with_filter(RequestFilter)
        self.assertTrue(self.handler in handlers)


class LoggingFiltersTest(TestCase):
    def setUp(self, *args, **kwargs):
        super(LoggingFiltersTest, self).setUp(*args, **kwargs)
        self.factory = RequestFactory()

    def test_import(self):
        import django_requestlogging.logging_filters
        reload(django_requestlogging.logging_filters)

    def test_request_filter(self):
        request = self.factory.get('/')
        record = logging.LogRecord('request_filter', 1, '/fake/path', 123,
                                   'test message', (), None)
        request.user = User.objects.create_user(username='test',
                                                password='test',
                                                email='test@example.com')
        rf = RequestFilter(request)
        self.assertTrue(rf.filter(record))
        self.assertEqual('127.0.0.1', record.remote_addr)
        self.assertEqual('test', record.username)
        self.assertEqual('GET', record.request_method)
        self.assertEqual('/', record.path_info)
        self.assertEqual('HTTP/1.1', record.server_protocol)
        self.assertEqual('-', record.http_user_agent)
        self.assertEqual('test message', record.msg)

    def test_unbound(self):
        record = logging.LogRecord('request_filter', 1, '/fake/path', 123,
                                   'test message', (), None)
        apf = RequestFilter()
        self.assertTrue(apf.filter(record))
        self.assertEqual('-', record.remote_addr)
        self.assertEqual('-', record.username)
        self.assertEqual('-', record.request_method)
        self.assertEqual('-', record.path_info)
        self.assertEqual('-', record.server_protocol)
        self.assertEqual('-', record.http_user_agent)
        self.assertEqual('test message', record.msg)

    def test_request_data_is_preserved(self):
        request = self.factory.get('/')
        record = logging.LogRecord('request_filter', 1, '/fake/path', 123,
                                   'test message', (), None)
        request.user = User.objects.create_user(username='test',
                                                password='test',
                                                email='test@example.com')
        unbound = RequestFilter()
        unbound.filter(record)
        bound = RequestFilter(request)
        bound.filter(record)
        self.assertEqual('127.0.0.1', record.remote_addr)
        self.assertEqual('test', record.username)
        self.assertEqual('GET', record.request_method)
        self.assertEqual('/', record.path_info)
        self.assertEqual('HTTP/1.1', record.server_protocol)
        self.assertEqual('-', record.http_user_agent)
        self.assertEqual('test message', record.msg)
