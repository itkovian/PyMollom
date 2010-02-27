#!/usr/bin/env python

# Mollom is a module that allows interacting with the Mollom
# content filtering service.
# Copyright (C) 2008-2010 Andy Georges
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
# 
# Update 2008-09-09: MollomAPI.getServerList should now check if the 
#                    list by the server is empty. If that's the case, 
#                    a hardcoded list of servers should be used.

""" Mollom is a module that allows interacting with the Mollom
    content filtering service.
"""

import sys
import random
import hashlib
import hmac
import base64
import time
from datetime import datetime
from datetime import timedelta
import xmlrpclib as x
from HTTPTransport import HTTPTransport
from ConfigParser import ConfigParser

    
class MollomFault(object):
  """MollomFault encapsulates values returned by the Mollom service that indicate a fault."""

  MOLLOM_INTERNAL_ERROR = 1000
  MOLLOM_REFRESH        = 1100
  MOLLOM_SERVER_BUSY    = 1200

  def __init__(self, fault):
    super(MollomFault, self).__init__()
    self.xmlrpc_fault = fault

  def requiresRefresh(self):
    return self.xmlrpc_fault.faultCode == MollomFault.MOLLOM_REFRESH

  def serverBusy(self):
    return self.xmlrpc_fault.faultCode == MollomFault.MOLLOM_SERVER_BUSY



    
class MollomAPI(object):
  """MollomAPI is a class providing access to the Mollom (http://mollom.com) content filtering
     service.  """
  serverListInfo = None

  def __init__(self, publicKey, privateKey, cacheCallback = None, timeoutDays = 7, timeoutHours = 0, defaultServer = 'http://xmlrpc.mollom.com', defaultVersion = '1.0'):
    """MollomAPI constructor.

    Keyword arguments:
    publicKey                 -- The public Mollom key for your website.
    privateKey                -- The private Mollom key for your website.
    cacheCallback  (optional) -- The callback for storing/cacheing the server list. If not provided, the 
                                 list will be stored in a class variable
    timeoutDays    (optional) -- The Mollom server list timeout in days. Defaults to 7 days.
    timeoutHours   (optional) -- The Mollom server list timeout in hours. Defaults to 0 hours.
    defaultServer  (optional) -- The default server for communicating with Mollom. This should 
                                 only be used for obtaining a valid server list. Defaults to
                                 http://xmlrpc.mollom.com.
    defaultVersion (optional) -- The default API version used. Defaults to 1.0.

    The actual timeout is computed as the number of days plus the number of hours.
    """

    super(MollomAPI, self).__init__()
    self.privateKey = privateKey
    self.publicKey = publicKey

    self.cacheCallback = cacheCallback
    self.timeoutDays   = timeoutDays
    self.timeoutHours  = timeoutHours

    # maximal number of retries to access the service before bailing 
    self.__maxDepth = 5

    self.defaultServer = defaultServer 
    self.currentServer = defaultServer
    self.mollomVersion = defaultVersion

    self.hardCodedServerList = ['http://xmlrpc3.mollom.com', 'http://xmlrpc2.mollom.com', 'http://xmlrpc1.mollom.com']

  def __s(self):
    r = x.ServerProxy(self.currentServer + '/' + self.mollomVersion, HTTPTransport())
    return r

  def __authentication(self):
    """Computes the required authentication information for each message sent to the
    Mollom service. This function should not be used by other methods than the API 
    methods in the MollomAPI class.
    """

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000+0200",time.localtime())

    nonce = long(random.randint(0,0xffffffff)) << 32 | random.randint(0,0xffffffff)
    hash = hmac.new(self.privateKey, ":".join([timestamp, str(nonce), self.privateKey]), hashlib.sha1)

    data = dict()
    data['public_key']  = self.publicKey
    data['time'] = timestamp
    data['hash'] = base64.b64encode(hash.digest())
    data['nonce'] = str(nonce)

    return data


  def getServerList(self, useHardCodedList = False):
    """Obtain a list of available servers for sending the Mollom requests to.

    Mollom provides a number of servers to allow clients to operate event in
    the case a server goes down, by using the next server in line. The first
    server provided is the one that should preferably be used.

    In case of failure, we use a hard coded list of servers, but we only do this
    once, i.e., upon further requests, we only try to fetch a new list from the 
    server, rather than retrying the hard coded list.

    In case a cache callback was defined to store the server list, we use that,
    otherwise, we maintain a copy in a class variable.
    """

    # if there is a callback defined, we fetch from the cache
    if not self.cacheCallback is None:
      _serverListInfo = self.cacheCallback()
    else:
      _serverListInfo = self.__class__.serverListInfo

    print "DEBUG: _serverListInfo = ", _serverListInfo

    # This is not required by the API document, yet it makes sense to check 
    # the age of the cached server list, otherwise the chance exists we will
    # have to update anyway.
    if _serverListInfo is not None:
      (list_datetime, servers) = _serverListInfo
      # check if the list is not too old
      if datetime.now() < list_datetime + timedelta(days = self.timeoutDays, hours = self.timeoutHours):
        self.__class__.serverListInfo = _serverListInfo
        return servers

    data = self.__authentication()

    print "DEBUG: hardCodedServerList = ", self.hardCodedServerList

    # first, set the list to the hardcoded list
    for server in self.hardCodedServerList:
      self.currentServer = server
      try:
        response = self.__s().mollom.getServerList(data)
        _serverListInfo = (datetime.now(), response)
        if not self.cacheCallback is None:
          self.cacheCallback(listInfo = _serverListInfo)
        else:
          self.__class__.serverListInfo = _serverListInfo
        return response
      except x.Fault, fault:
          pass
      except x.ProtocolError, error:
          pass

    return None


  def __service(self, remote_call, data_, depth=0):
    """Makes the actual call to the Mollom service.

    The call is made to the first available server. This method automatically
    refreshes the server list in case no servers are available, as indicated 
    by a fault. After 5 refreshes, the method bails, returning None. This 
    method should only be called by the MollomAPI methods.

    Keyword arguments:
    remote_call            -- The name of the Mollom call to make.
    data_                  -- Dictionary containing the arguments for the call.
    depth       (optional) -- The recursive depth in case we need to refresh the
                              server list. 
  
    Returns:
      The result of the call, if a server is available.
      None after 5 successive refreshes of the server list.
    """
    
    data = self.__authentication()
    data.update(data_)

    #if we tried too many times, give up
    if depth > self.__maxDepth:
      return None

    #try the remote call on each of the servers from the obtained list. 
    for server in self.getServerList():
      try:
        #print "DEBUG: contacting server: %s"%(server)
        self.currentServer = server
        s = self.__s()
        response = eval('s.mollom.' + remote_call + '(data)')
        return response
      except x.Fault, fault:
        mf = MollomFault(fault)
        if mf.requiresRefresh():
          if not self.getServerList() is None:
            return self.__service(remote_call, data_, depth+1)
        elif mf.serverBusy():
          pass
        else:
          pass
      except x.ProtocolError, error:
        return error

    if not self.getServerList(True) is None:
      return self.__service(remote_call, data_, depth+1)

    return None


  def checkContent(self, sessionID=None, postTitle=None, postBody=None, authorName=None, authorURL=None, authorMail=None, authorOpenID=None, authorIP=None, authorID=None):
    """Submit content to the Mollom service to have it checked for spaminess.

    Keyword arguments:
    sessionID    (optional) -- The session ID that Mollom uses to identify chunks of communication
                               on the same piece of content. The ID is provided by Mollom, so the first
                               call to the service should have no sessionID set.
    postTitle    (optional) -- The title of your post or comment.
    postBody     (optional) -- The main content that needs to be checked.
    authorName   (optional) -- The content author.
    authorURL    (optional) -- The URL of the content author's website.
    authorMail   (optional) -- The email address of the content author.
    authorOpenID (optional) -- The Open ID of the content author.
    authorIP     (optional) -- The IP address of the content author.
    authorID     (optional) -- The ID the content author has on the website where the posting takes place.

    Returns:
    A dictionary with following keys if succesful
      spam       -- 1 for ham, 2 for spam, 3 for unsure
      quality    -- Mollom's assesment of the content quality [0,1]
      session_id -- The session ID for communicating with Mollom about this chunk of content
    """

    data = dict()

    if sessionID is not None: data['session_id'] = sessionID
    if postTitle is not None: data['post_title'] = postTitle
    if postBody is not None: data['post_body'] = postBody 
    if authorName is not None: data['author_name'] = authorName 
    if authorURL is not None: data['author_url'] = authorURL
    if authorMail is not None: data['author_mail'] = authorMail 
    if authorOpenID is not None: data['author_openid'] = authorOpenID
    if authorIP is not None: data['author_ip'] = authorIP
    if authorID is not None: data['author_id'] = authorID

    return self.__service('checkContent', data)


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
    self.api = MollomAPI(publicKey = self.publicKey, privateKey = self.privateKey, timeoutDays = self.timeoutDays, timeoutHours = self.timeoutHours, cacheCallback = self.cacheServerList)

  def cacheServerList(self, listInfo = None):
    if not listInfo is None:
      self.listInfo = listInfo
    return self.listInfo

  def getServerList(self):
    return self.api.getServerList()

  def checkContent(self, sessionID=None, postTitle=None, postBody=None, authorName=None, authorURL=None, authorMail=None, authorOpenID=None, authorIP=None, authorID=None):
    return self.api.checkContent(sessionID, postTitle, postBody, authorName, authorURL, authorMail, authorOpenID, authorIP, authorID)

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
