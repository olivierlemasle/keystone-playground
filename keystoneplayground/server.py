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

import os

from paste.deploy import loadapp
from paste import httpserver

from oslo_config import cfg

CONF = cfg.CONF


class Server(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def serve(self):
        config_file = 'keystone-playground-paste.ini'
        config_file_path = CONF.find_file(config_file)
        config_file_path = os.path.abspath(config_file_path)
        app = loadapp("config:%s" % config_file_path)
        httpserver.serve(app, host=self.host, port=self.port)
