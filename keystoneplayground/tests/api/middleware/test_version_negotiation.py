# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from six.moves import http_client
import webob

from keystoneplayground.api.middleware import version_negotiation
from keystoneplayground.tests import base


class TestVersionNegotiationFilter(base.TestCase):

    def test_accept_header_with_serialization_format(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {'Accept': 'application/vnd.openstack.keystoneplayground.v1+json'}
        request = webob.Request.blank('/test', headers=h)
        middleware.process_request(request)
        self.assertEqual(1,
                         request.environ['api.version'])
        self.assertEqual('/v1/test',
                         request.path_info)

    def test_accept_header_without_serialization_format(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {'Accept': 'application/vnd.openstack.keystoneplayground.v1'}
        request = webob.Request.blank('/test', headers=h)
        middleware.process_request(request)
        self.assertEqual(1,
                         request.environ['api.version'])
        self.assertEqual('/v1/test',
                         request.path_info)

    def test_accept_header_no_version(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {'Accept': 'application/vnd.openstack.keystoneplayground+json'}
        request = webob.Request.blank('/v1/test', headers=h)
        middleware.process_request(request)
        self.assertEqual(1,
                         request.environ['api.version'])
        self.assertEqual('/v1/test',
                         request.path_info)

    def test_accept_header_unknown_mediatype(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {'Accept': 'application/json'}
        request = webob.Request.blank('/v1/test', headers=h)
        middleware.process_request(request)
        self.assertEqual(1,
                         request.environ['api.version'])
        self.assertEqual('/v1/test',
                         request.path_info)

    def test_no_header(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {}
        request = webob.Request.blank('/v1/test', headers=h)
        middleware.process_request(request)
        self.assertEqual(1,
                         request.environ['api.version'])
        self.assertEqual('/v1/test',
                         request.path_info)

    def test_no_version(self):
        middleware = version_negotiation.VersionNegotiationFilter(None)
        h = {'Accept': 'application/json'}
        request = webob.Request.blank('/test', headers=h)
        app = middleware.process_request(request)
        self.assertEqual(http_client.MULTIPLE_CHOICES,
                         app.__call__(request).status_code)
