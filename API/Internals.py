#!/usr/bin/env python

# Mollom is a module that allows interacting with the Mollom
# content filtering service.
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
__author__ = 'Andy Georges'
__status__ = 'beta'
__version__ = '0.1'
__date__ = 'Feb 8, 2012'

# This module contains internal functions
# ---------------------------------------------------------------------

import oauth2
import urllib


def __service(method, path, data=None, maxRetries=0, depth=0):
    """The service method makes the actual call to the Mollom service
    on behalf of the public API method.

    @type method: the HTTP method (POST, GET, ...)
    @type path: the URL path
    @type data: dictionary with the data to pass in case of a POST
    @type maxRetries: int
    @type depth:int

    @returns:
     - The result of the call, if a server is available.
     - None after MOLLOM_RETRIES successive failed retries.
    """

    if depth > maxRetries:
        return None

        # superfluous?
        #params = { 'oauth_version': 1.0
        #         , 'oauth_timestamp': int(time.time())
        #         , 'oauth_nonce': oauth2.generate_nonce()
        #         , 'oauth_signature_method': "HMAC-SHA1"
        #         , 'oauth_consumer_key': self.publicKey
        #         }

    body = urllib.urlencode(data)
    consumer = oauth2.Consumer(key=self.publicKey, secret=self.privateKey)
    client = oauth2.Client(consumer)

    #request = oauth2.Request( method='GET'
    #                        , url= self.mollomServer + path
    #                        , parameters = params
    #                        , body = body)

    resp, content = client.request(self.mollomServer + path, method, headers=self.mollomHeaders, body=body)

    if resp.status == 200:
        return content
    else:
        # FIXME: do some error checking here
        return None


def __cat_maybe_values(d):
    d_ = dict()
    for k,v in d.iteritems():
        if v != None:
            d_[k] = v
    return d_