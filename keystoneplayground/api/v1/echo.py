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

from oslo_serialization import jsonutils
from six.moves import http_client
import webob.dec


class Controller(object):

    """echo controller"""

    def index(self, req):
        headers = req.headers.items()

        response = webob.Response(request=req,
                                  status=http_client.OK,
                                  content_type='application/json')
        response.body = jsonutils.dumps(dict(headers=headers))
        return response

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        return self.index(req)


def create_resource():
    return Controller()
