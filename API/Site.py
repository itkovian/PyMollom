#!/usr/bin/env python
#
# Copyright (C) 2008-2012 Andy Georges
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ---------------------------------------------------------------------
__author__ = "Andy Georges"
__date__ = '$Apr 20, 2012'
# This module contains the class file for the Mollom Site API
# ---------------------------------------------------------------------

from httplib2 import HTTP
from json import JSONDecoder
from urllib import urlencode

from PyMollom import *


class SiteResponse(MollomResponse):
    """Response obtained from the Site API."""

    def __init__( self
                , id
                , public_key
                , private_key
                , url
                , email
                , languages
                , subscription
                , platform_name
                , platform_version
                , client_name
                , client_version):
        """Initialise instance."""
        self.id = id
        self.public_key = public_key
        self.private_key = private_key
        self.url = url
        self.email = email
        self.languages = languages
        self.subscription = subscription
        self.platform_name = platform_name
        self.platform_version = platform_version
        self.client_name = client_name
        self.client_version = client_version

    def fromJSON(self, js):
        """Convert a JSON string to the corresponding SiteResponse."""
        return SiteReponse( id=js.get('id')
                          , public_key=js.get('publicKey')
                          , private_key=js.get('privateKey')
                          , url=js.get('url')
                          , email=js.get('email')
                          , languages=js.get('languages')
                          , subscription=js.get('subscription')
                          , platform_name=js.get('platformName')
                          , platform_version=js.get('platformVersion')
                          , client_name=js.get('clientName')
                          , client_version=js.get('clientVersion')
        )


class Site(MollomBase):
    """Implementation of the API calls for a site.
    """

    def __init__(self, public_key, private_key):
        super(MollomBase, self).__init__(public_key, private_key)

    def create( self
              , url
              , email
              , languages
              , platform_name
              , platform_version
              , client_name
              , client_version):
        """Creates a new site in the Mollom system.

        @type url: string -- URL of the website to protect
        @type email: string -- email address of the primary site contact
        @type languages: [string] -- list of ISO codes of languages
        @type platform_name: string -- for example, Drupal
        @type platform_version: string -- for example, 7.1
        @type client_name: string -- name of the plugin used to communicate with Mollom, e.g. PyMollom
        @type client_version: string -- version of said client

        @returns SiteResponse instance with the fields filled in

        This method does not use the default __service, since there is no public or private key available
        when registering a site with Mollom.
        """
        data = {
            'url': url,
            'email': email,
            'languages': languages,
            'platformName': platform_name,
            'platformVersion': platform_version,
            'clientName': client_name,
            'clientVersion': client_version,
        }
        h = HTTP()
        path = "%s/%s/site" % (MOLLOM_SERVER, MOLLOM_VERSION)
        response, content = h.request(path, "POST", urlencode(data))
        ## FIXME: check response
        if response['status'] == 200:
            return(SiteReponse().fromJSON(JSONDecoder().decode(content)['site']))
        else:
            if response['status'] == 401:
                raise UnauthorisedError(401, 'Not authorised to create a new site')
            elif response['status'] == 403:
                raise ForbiddenError(403, 'Access forbidden to %s' % (path))
            elif response['status'] == 404:
                raise NotFoundError(404, 'Resource not found %s' % (path))
            else:
                raise MollomError(response['status'], "Borked")

    def update( self
              , url
              , email
              , languages
              , platform_name
              , platform_version
              , client_name
              , client_version):
        """Updates a site in the Mollom system and/or verifies the key-pair

        @type url: string -- URL of the website to protect
        @type email: string -- email address of the primary site contact
        @type languages: [string] -- list of ISO codes of languages
        @type platform_name: string -- for example, Drupal
        @type platform_version: string -- for example, 7.1
        @type client_name: string -- name of the plugin used to communicate with Mollom, e.g. PyMollom
        @type client_version: string -- version of said client

        @returns SiteResponse instance with the fields filled in
        """
        data = {
            'url': url,
            'email': email,
            'languages': languages,
            'platformName': platform_name,
            'platformVersion': platform_version,
            'clientName': client_name,
            'clientVersion': client_version,
        }
        h = HTTP()
        path = "%s/%s/site/%s" % (MOLLOM_SERVER, MOLLOM_VERSION, self.public_key)
        (response, content) = h.request( uri=path
                                       , method="POST"
                                       , data=urlencode(data)
                                       , headers={'Accept': 'application/json;q=0.8, */*;q=0.5'})
        if response['status'] == 200:
            return(SiteReponse().fromJSON(JSONDecoder().decode(content)['site']))
        else:
            if response['status'] == 401:
                raise UnauthorisedError(401, 'Not authorised to create a new site')
            elif response['status'] == 403:
                raise ForbiddenError(403, 'Access forbidden to %s' % (path))
            elif response['status'] == 404:
                raise NotFoundError(404, 'Resource not found %s' % (path))
            else:
                raise MollomError(response['status'], "Borked")


    def read(self):
        """Get the information Mollom keeps about the given site."""
        path = 'site/%s' % (self.public_key)
        try:
            content = __service('GET', path)
            return(SiteReponse().fromJSON(JSONDecoder().decode(content)['site']))
        except MollomError, m_err:
            raise

    def delete(self):
        """Delete the site from Mollom."""
        path = 'site/%s/delete' % (self.public_key)
        try:
            content = __service('POST', path)
            return(SiteReponse().fromJSON(JSONDecoder().decode(content)['site']))
        except MollomError, m_err:
            raise

    def list(self, offset=0, count=None):
        """List all sites registered with Mollom that correspond to the given authentication."""
        data = {
            'offset': offset
        }
        if not count is None:
            data['count'] = count
        path = 'site/'
        try:
            content = __service('GET', path, data)
            jd = JSONDecoder().decode(content)
            sites = jd['list']
            listCount = jd['listCount']
            listOffset = jd['listOffset']
            listTotal = jd['listTotal']
            return [SiteReponse().fromJSON(s) for s in sites]
        except MollomError, m_err:
            raise

