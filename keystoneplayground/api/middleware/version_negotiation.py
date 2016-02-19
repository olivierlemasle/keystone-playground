#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
A filter middleware that inspects the requested URI for a version string
and/or Accept headers and attempts to negotiate an API controller to
return
"""

from oslo_config import cfg
from oslo_log import log as logging

from keystoneplayground.api import versions
from keystoneplayground.common import wsgi

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class VersionNegotiationFilter(wsgi.Middleware):

    def __init__(self, app):
        self.versions_app = versions.Controller()
        self.vnd_mime_type = 'application/vnd.openstack.keystoneplayground.'
        super(VersionNegotiationFilter, self).__init__(app)

    def process_request(self, req):
        """Try to find a version first in the accept header, then the URL."""
        LOG.debug(("Determining version of request:{method} {path} "
                   "Accept: {accept}").format(method=req.method,
                                              path=req.path,
                                              accept=req.accept))

        req_version = self._get_version_from_header(req)
        if req_version:
            LOG.debug("Using media-type versioning")

        else:
            LOG.debug("Using url versioning")
            # Remove version in url so it doesn't conflict later
            req_version = self._pop_path_info(req)

        try:
            version = self._match_version_string(req_version)
        except ValueError:
            LOG.warning("Unknown version. Returning version choices.")
            return self.versions_app

        req.environ['api.version'] = version
        req.path_info = ''.join(('/v', str(version), req.path_info))
        LOG.debug("Matched version: v{version}".format(version=version))
        LOG.debug('new path {path}'.format(path=req.path_info))
        return None

    def _get_version_from_header(self, req):
        accept = str(req.accept)
        if accept.startswith(self.vnd_mime_type):
            # Example: application/vnd.openstack.keystoneplayground.v1+json
            token_loc = len(self.vnd_mime_type)
            idx_suffix = accept.rfind('+')
            if idx_suffix == -1:
                return accept[token_loc:]
            else:
                return accept[token_loc:idx_suffix]
        else:
            return None

    def _match_version_string(self, subject):
        """Given a string, tries to match a major and/or minor version number.

           :param subject: The string to check
           :returns version found in the subject
           :raises ValueError if no acceptable version could be found
        """
        if subject in ('v1',):
            major_version = 1
        else:
            raise ValueError()
        return major_version

    def _pop_path_info(self, req):
        """'Pops' off and return the next segment of PATH_INFO

            Do NOT push it onto SCRIPT_NAME.
        """
        path = req.path_info
        if not path:
            return None
        while path.startswith('/'):
            path = path[1:]
        idx = path.find('/')
        if idx == -1:
            idx = len(path)
        r = path[:idx]
        req.path_info = path[idx:]
        return r
