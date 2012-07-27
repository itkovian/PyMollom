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

"""Implementation of the Mollom REST API.

@author Andy Georges
@date April 24, 2012
"""

__author__ = 'Andy Georges'
__status__ = 'beta'
__version__ = '0.1'
__date__ = 'April 24, 2012'


import API.Content as Content

__all__ = [Content]


MOLLOM_SERVER="http://rest.mollom.com/"
MOLLOM_VERSION="v1"


class MollomBase(object):
    """Base class for the Mollom API classes.
    """
    def __init__(self, public_key, private_key):
        """Initialise."""
        self.public_key = public_key
        self.private_key = private_key
        self.mollom_headers = {'Accept': 'application/json;q=0.8, */*;q=0.5'}
        self.mollom_uri = "%s/%s" % (MOLLOM_SERVER, MOLLOM_VERSION)


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
        consumer = oauth2.Consumer(key=self.public_key, secret=self.private_key)
        client = oauth2.Client(consumer)

        #request = oauth2.Request( method='GET'
        #                        , url= self.mollomServer + path
        #                        , parameters = params
        #                        , body = body)

        resp, content = client.request(self.mollom_uri + path, method, headers=self.mollom_headers, body=body)

        if resp.status == 200:
            return content
        else:
            # FIXME: do some error checking here
            return None


class MollomError(Exception):
    """Base class for all Mollom errors.

    In general, the following status codes result in errors:

    401 - Unauthorised
    403 - Forbidden
    404 - Not Found

    These errors may have more specific meaning when used in
    the different APIs.
    """
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "Mollom error [%d] - %s" % (self.code, self.message)


class ConnectionError(MollomError):
    pass

class BlacklistError(MollomError):
    pass


class CaptchaError(MollomError):
    CAPTCHA_DOES_NOT_EXIST = 404
    CAPTCHA_ALREADY_PROCESSED = 409
    CAPTCHA_EXPIRED = 410

    def __init__(self, code, message):
        super(CaptchaError, self).__init__(code, message)

class CaptchaDoesNotExistError(CaptchaError):
    def __init__(self, code, message):
        super(CaptchaDoesNotExist, self).__init__(code, message)

class CaptchaAlreadyProcessedError(CaptchaError):
    def __init__(self, code, message):
        super(CaptchaAlreadyProcessed, self).__init__(code, message)

class CaptchaExpiredError(CaptchaError):
    def __init__(self, code, message):
        super(CaptchaExpired, self).__init__(code, message)


class ContentError(MollomError):
    def __init__(self, code, message):
        super(ContentError, self).__init__(code, message)


class FeedbackError(MollomError):
    FEEDBACK_MISSING_ID = 400
    FEEDBACK_UNKNOWN_REASON = 400

    def __init__(self, code, message)
        super(FeedbackError, self).__init__(code, message)

class FeedbackMissingIdError(FeedbackError):
    def __init__(self, code, message):
        super(FeedbackMissingIdError, self).__init__(code, message)

class FeedbackUnknownReasonError(FeedbackError):
    def __init__(self, code, message):
        super(FeedbackUnknownReasonError, self).__init__(code, message)

class SiteError(MollomError):
    SITE_UNKNOWN = 404

    def __init__(self, code, message):
        super(SiteError, self).__init__(code, message)


class SiteUnknownError(SiteError):
    def __init__(self, code, message):
        super(SiteUnknownError, self).__init__(code, mesage)



class WhitelistError(MollomError):
    WHITELIST_ENTRY_UNKNOW

    def __init__(self, code, message):
        super(WhitelistError, self).__init__(code, message)


class WhitelistUnknownEntryError(WhitelistError):
    def __init__(self, code, message):
        super(WhitelistUnknownEntryError, self).__init__(code, message)


class Unauthorised(MollomError):
    pass

class Forbidden(MollomError):
    pass

class NotFound(MollomError):
    pass

class JSONParseError(MollomError):
    pass




