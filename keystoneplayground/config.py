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

import sys

from oslo_config import cfg

import keystoneplayground

keystoneplaygroundOpts = [
    cfg.StrOpt('host',
               default='0.0.0.0',
               help='Hostname for Keystone Playground API'),
    cfg.StrOpt('port',
               default='8081',
               help='Port for Keystone Playground API')
]

keystoneplaygroundGroup = cfg.OptGroup(name='keystoneplayground',
                                       title='Keystone Playground settings',
                                       help='AKeystone Playground settings')

CONF = cfg.CONF
CONF.register_opts(keystoneplaygroundOpts, group=keystoneplaygroundGroup)


def parse_args(args=None, usage=None, default_config_files=None):
    CONF(args=sys.argv[1:],
         project='keystoneplayground',
         version=keystoneplayground.__version__,
         usage=usage,
         default_config_files=default_config_files)
