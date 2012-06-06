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
__author__ = "Andy Georges"
__date__ = "$Feb 8, 2012$"
# This module contains the main Mollom classes
# ---------------------------------------------------------------------


""" Mollom is a module that allows interacting with the Mollom
    content filtering service.

    The below implementation supports the REST API as defined by
    http://mollom.cm/api/rest.
"""

import json
import oauth2
import urllib
from ConfigParser import ConfigParser

from PyMollom import *

class MollomBase(object):
    """Base class for the Mollom API classes.
    """
    def __init__(self, public_key, private_key):
        """Initialise."""
        self.public_key = public_key
        self.private_key = private_key
        self.mollom_headers = ['Accept':'application/json;q=0.8, */*;q=0.5']
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


class MollomAPI(object):
    """MollomAPI is a class providing access to the Mollom (http://mollom.com) content filtering
    service.
    """

    APIVersion = 'v1'
    mollomServer = 'http://dev.mollom.com/' + APIVersion + '/'
    mollomHeaders = {'Accept': 'application/json;q=0.8'
        , 'Content-Type': 'application/x-www-form-urlencoded'}

    MOLLOM_RETRIES = 2


    def __init__(self, publicKey, privateKey, timeoutDays=7, timeoutHours=0, defaultServer='http://rest.mollom.com',
                 defaultVersion='1.0'):
        """MollomAPI constructor.

        Keyword arguments:
        publicKey                 -- The public Mollom key for your website.
        privateKey                -- The private Mollom key for your website.
        timeoutDays    (optional) -- The Mollom server list timeout in days. Defaults to 7 days.
        timeoutHours   (optional) -- The Mollom server list timeout in hours. Defaults to 0 hours.
        defaultServer  (optional) -- The default server for communicating with Mollom. This should
                                     only be used for obtaining a valid server list. Defaults to
                                     http://rest.mollom.com.
        defaultVersion (optional) -- The default API version used. Defaults to 1.0.

        The actual timeout is computed as the number of days plus the number of hours.
        """

        super(MollomAPI, self).__init__()
        self.privateKey = privateKey
        self.publicKey = publicKey

        self.timeoutDays = timeoutDays
        self.timeoutHours = timeoutHours

        # maximal number of retries to access the service before bailing
        self.__maxDepth = 5

        self.mollomVersion = defaultVersion


    def sendFeedback(self, sessionID, feedback):
        """Provide Mollom with feedback on the decision it made about the content.

        Keyword arguments:
        sessionID -- The session ID that Mollom uses to identify the content feedback is
                     given for. The actual value is provided by Mollom when a checkContent
                     call is made.
        feedback  -- The feedback you wish to provide as a string taking four possible values:
                     'spam', 'profanity', 'low-quality', 'unwanted'. It is important to know
                     that Mollom will use feedback to update the reputation assigned to
                     your key-pair.

        Returns:
        True when the call is succesfull
        """

        data = dict()
        data['session_id'] = sessionID
        data['feedback'] = feedback

        return self.__service('sendFeedback', data)


    def getImageCaptcha(self, sessionID=None, authorIP=None):
        """Instruct the Mollom service to generate an image CAPTCHA.

        Keyword arguments:
        sessionID (optional) -- The session ID that Mollom uses to identify the content the CAPTCHA
                                is requested for. If it is available it should be provided.
        authorIP  (optional) -- The IP address of the user who generated the content.

        Returns:
        A dictioary with following keys if succesfull:
          session_id -- The session ID associated with this particular CAPTCHA (may be different from the
                        session ID corresponding to the content.
          url        -- The URL where the CAPTCHA can be obtained.
        """

        data = dict()

        if sessionID is not None: data['session_id'] = sessionID
        if authorIP is not None: data['author_ip'] = authorIP

        return self.__service('getImageCaptcha', data)


    def getAudioCaptcha(self, sessionID=None, authorIP=None):
        """Instruct the Mollom service to generate an audio CAPTCHA.

        Keyword arguments:
        sessionID (optional) -- The session ID that Mollom uses to identify the content the CAPTCHA
                                is requested for. If it is available it should be provided.
        authorIP  (optional) -- The IP address of the user who generated the content.

        Returns:
        A dictioary with following keys if succesfull:
          session_id -- The session ID associated with this particular CAPTCHA (may be different from the
                        session ID corresponding to the content.
          url        -- The URL where the CAPTCHA can be obtained.
        """

        data = dict()

        if sessionID is not None: data['session_id'] = sessionID
        if authorIP is not None: data['author_ip'] = authorIP

        return self.__service('getAudioCaptcha', data)


    def checkCaptcha(self, sessionID, solution):
        """Verify the reponse given by the (human) user to the CAPTCHA Mollom generated.

        Keyword arguments:
        sessionID -- The session ID corresponding to the CAPTCHA.
        solution  -- The solution to the CAPTCHA.

        Returns:
          True if the solution is correct.
          False otherwise.
        """

        data = dict()

        data['session_id'] = sessionID
        data['solution'] = solution

        return self.__service('checkCaptcha', data)


    def getStatistics(self, type):
        """Obtain statistics from the Mollom service.

        Keyword arguments:
        type -- The type of statistics we want. There are several options depending
                on the string passed into this argument:
                  total_days: Number of days Mollom has been used
                  total_accepted: Total number of messages Mollom accepted as ham
                  total_rejected: Total number of messages Mollom rejected as spam
                  yesterday_accepted: Number of messages Mollom accepted as ham the previous day
                  yesterday_rejected: Number of messages Mollom rejected as spam the previous day
                  today_accepted: Number of messages Mollom accepted today
                  today_rejected: Number of messages Mollom rejected today.

        Returns:
          An integer indicating the requested number
        """

        data = dict()

        data['type'] = type

        return self.__service('getStatistics', data)


    def verifyKey(self):
        """Verify the status of your key.

        Returns:
          True for a valid key.
          False otherwise.
        """

        data = dict()

        return self.__service('verifyKey', data)

    def detectLanguage(self, text):
        """Detect the language the text is written in.

        Keyword arguments:
        text -- The text to run language detection on.

        Returns:
          Unclear from the API description, but likely an array of structs
          containing a language string (2 or 3 characters) and a confidence
          value between 0 and 1. The languages are sorted according to
          descending confidence values.
        """

        data = dict()
        data['text'] = text

        return self.__service('detectLanguage', data)

    def addBlacklistText(self, text, match, reason):
        """Add a piece of text to the blacklist for the site corresponding to
           the used public/private keypair

        Keyword arguments:
        text -- The text to blacklist
        match -- Method used to search for the text: one of 'exact', 'contains'
        reason -- One of the reasons for blacklisting the text: 'spam', 'profanity', 'low-quality', 'unwanted'

        Returns:
          Always returns true
        """
        data = dict()
        data['text'] = text
        data['match'] = match
        data['reason'] = reason

        return self.__service('addBlacklistText', data)

    def removeBlacklistText(self, text):
        """Remove a piece of blacklisted text

        Keyword arguments:
        text -- The text to remove from the blacklist

        Returns:
          Always returns true
        """
        data = dict()
        data['text'] = text

        return __service('removeBlacklistText', data)

    def listBlacklistText(self):
        """Return a list of the site-specific blacklisted text snippets.

        Returns:
          Unclear from the API description, but supposedly an array with
          all the snippets that have been blacklisted for the site with
          corresponding public key.
        """
        return self.__service('listBlacklistText', {})


    def addBlacklistURL(self, url):
        """Add an URL to the list of blacklisted URLS for the site corresponding to
           the used public/private keypair

        Keyword arguments:
        url -- The URL to blacklist

        Returns:
          Always returns true
        """
        data = dict()
        data['url'] = url

        return __service('addBlacklistURL', data)

    def removeBlacklistURL(self, url):
        """Remove an URL from the blacklisted URLs

        Keyword arguments:
        url -- The URL to remove

        Returns:
          Always returns true
        """
        data = dict()
        data['url'] = url

        return __service('removeBlacklistURL', data)

    def listBlacklistURL(self):
        """Return a list of the site-specific blacklisted URLs.

        Returns:
          An array containing the URLs with some meta-information. The Mollom API docs need to be checked.
        """
        return self.__service('listBlacklistURL', {})


class MollomContentResponse(object):
    """Encapsulating a response from a checkContent call."""

    def __init__(self, response):
        self.response = response

    def spam(self):
        return response['spam'] == 1

    def ham(self):
        return response['spam'] == 2

    def unsure(self):
        return response['spam'] == 3

    def quality(self):
        return response['quality']

    def sessionID(self):
        return response['session_id']


class MollomBase(object):
    """MollomBase provides baseline functionality encapsulating Mollom API calls.

    The configuration is put in a config file, which has the following mandatory and
    optional fields:

      [general]
      server      -- The main Mollom server, e.g., http://xmlrpc.mollom.com
      base_url    -- The URL of the website using the Mollom service

      [authentication]
      public key  -- The Mollom public key for your website
      private key -- The Mollom private key for your website

      [caching]
      max serverlist days  -- Maximum number of days we keep a list cached
      max serverlist hours -- Maximum number of hours we keep a list cached. The total time
                              is the sum of both.


    A user should derive the class and provide functionality for the cacheServerList()
    method, if desired.

    Note: this class is still in early draft stage, so may change frequently.
    """

    def __init__(self, configfile):
        super(MollomBase, self).__init__()
        self.config = ConfigParser([])
        self.config.read(configfile)
        self.privateKey = self.config.get('authentication', 'private key')
        self.publicKey = self.config.get('authentication', 'public key')

        self.timeoutDays = int(self.config.get('caching', 'max serverlist days'))
        self.timeoutHours = int(self.config.get('caching', 'max serverlist hours'))

        self.listInfo = None
        self.api = MollomAPI(publicKey=self.publicKey, privateKey=self.privateKey, timeoutDays=self.timeoutDays,
            timeoutHours=self.timeoutHours, cacheCallback=self.cacheServerList)

    def cacheServerList(self, listInfo=None):
        if not listInfo is None:
            self.listInfo = listInfo
        return self.listInfo

    def getServerList(self):
        return self.api.getServerList()

    def checkContent(self, sessionID=None, postTitle=None, postBody=None, authorName=None, authorURL=None,
                     authorMail=None, authorOpenID=None, authorIP=None, authorID=None):
        return self.api.checkContent(sessionID, postTitle, postBody, authorName, authorURL, authorMail, authorOpenID,
            authorIP, authorID)

    def sendFeedback(self, sessionID, feedback):
        return self.api.sendFeedback(sessionID, feedback)

    def getImageCaptcha(self, sessionID=None, authorIP=None):
        return self.api.getImageCaptcha(sessionID, authorIP)

    def getAudioCaptcha(self, sessionID=None, authorIP=None):
        return self.api.getAudioCaptcha(sessionID, authorIP)

    def checkCaptcha(self, sessionID, solution):
        return self.api.checkCaptcha(sessionID, solution)

    def getStatistics(self, type):
        return self.api.getStatistics(type)

    def verifyKey(self):
        return self.api.verifyKey()

    def detectLanguage(self, text):
        return self.api.detectLanguage(text)

    def addBlacklistText(self, text, match, reason):
        return self.api.addBlacklistText(text, match, reason)

    def removeBlacklistText(self, text):
        return self.api.removeBlacklistText(text)

    def listBlacklistText(self):
        return self.api.listBlacklistText()

    def addBlacklistURL(self, url):
        self.api.addBlacklistURL(url)

    def removeBlacklistURL(self, url):
        self.api.removeBlacklistURL(url)

    def listBlacklistURL(self):
        self.api.listBlacklistURL()
