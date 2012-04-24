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
__date__ = "$Feb 8, 2012$"
# This module contains the class file for the Mollom Content API
# ---------------------------------------------------------------------

import urllib

from Internals import __service, __cat_maybe_values

class Check(object):
    """Representing the checks Mollom is requested to make on a submitted piece of content:
    """
    SPAM = "spam"
    QUALITY = "quality"
    PROFANITY = "profanity"
    LANGUAGE = "language"
    SENTIMENT = "sentiment"


class Strictness(object):
    """Representing the strictness of a check.
    """
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"


class ContentError(MollomFault):
    pass


class Content(object):
    def __init__(self):
        self.contentId = None

    def __parseContentResponse(self, js):
        """Parses the returned answer from a Content API call.

        For now, this simply returns a dict with the fields as keys
        """
        return js['content']


    def checkContent( self
                      , post_title=None
                      , post_body=None
                      , author_name=None
                      , author_url=None
                      , author_mail=None
                      , author_open_id=None
                      , author_ip=None
                      , author_id=None
                      , checks=None
                      , unsure=None
                      , strictness=None
                      , rateLimit=None
                      , honeypot=None
                      , stored=None
                      , url=None
                      , context_url=None
                      , context_title=None
    ):
        """Submit content to the Mollom service to have it checked for spaminess.

        Keyword arguments:
        post_title     (optional) -- The title of your post or comment.
        post_body      (optional) -- The main content that needs to be checked.
        author_name    (optional) -- The content author.
        author_url     (optional) -- The URL of the content author's website.
        author_mail    (optional) -- The email address of the content author.
        author_open_id (optional) -- The Open ID of the content author.
        author_ip      (optional) -- The IP address of the content author.
        author_id      (optional) -- The ID the content author has on the website where the posting takes place.
        checks         (optional) --
        unsure         (optional) --
        strictness     (optional) --
        honeypot       (optional) --
        stored         (optional) --
        url            (optional) --
        context_url    (optional) --
        context_title  (optional) --

        Returns:
        A dictionary with following keys if succesful
            id                  -- the content ID corresponding to the submission
            spamScore           -- only returned when the check included SPAM
        """

        tuples = {'postTitle': post_title
            , 'postBody': post_body
            , 'authorName': author_name
            , 'authorUrl': author_url
            , 'authorMail': author_mail
            , 'authorOpenid': author_open_id
            , 'checks': checks #FIXME: these should be concatenated
            , 'unsure': unsure
            , 'strictness': strictness
            , 'honeypot': honeypot
            , 'stored': stored
            , 'url': url
            , 'contextUrl': context_url
            , 'contextTitle': context_title}
        data = __cat_maybe_values(tuples)
        answer = __service('POST', 'content', data, )

        # for now, we check for a None, this should be fixed when we throw exceptions
        if answer == None:
            return None

        return self.__parseContentResponse(json.loads(answer))

    def updateContent( self
                       , post_title=None
                       , post_body=None
                       , author_name=None
                       , author_url=None
                       , author_mail=None
                       , author_open_id=None
                       , author_ip=None
                       , author_id=None
                       , checks=None
                       , unsure=None
                       , strictness=None
                       , rateLimit=None
                       , honeypot=None
                       , stored=None
                       , url=None
                       , context_url=None
                       , context_title=None
    ):
        """Submit content to the Mollom service to have it updated. The contentId is
        taken from the calling object, so you should not use this unless you called
        checkContent first.

        Keyword arguments:
        post_title    (optional) -- The title of your post or comment.
        post_body     (optional) -- The main content that needs to be checked.
        author_name   (optional) -- The content author.
        author_url    (optional) -- The URL of the content author's website.
        authorMail   (optional) -- The email address of the content author.
        authorOpenid (optional) -- The Open ID of the content author.
        authorIp     (optional) -- The IP address of the content author.
        authorId     (optional) -- The ID the content author has on the website where the posting takes place.
        checks       (optional) --
        unsure       (optional) --
        strictness   (optional) --
        honeypot     (optional) --
        stored       (optional) --
        url          (optional) --
        contextUrl   (optional) --
        contextTitle (optional) --

        Returns:
        A dictionary with following keys if succesful
          spam       -- 1 for ham, 2 for spam, 3 for unsure
          quality    -- Mollom's assesment of the content quality [0,1]
          session_id -- The session ID for communicating with Mollom about this chunk of content
        """

        # FIXME: throw an exception
        if self.contentId == None:
            return None

        tuples = {'contentId': self.contentId
            , 'post_title': post_title
            , 'post_body': post_body
            , 'author_name': author_name
            , 'author_url': author_url
            , 'authorMail': author_mail
            , 'authorOpenid': author_open_id
            , 'checks': checks #FIXME: these should be concatenated
            , 'unsure': unsure
            , 'strictness': strictness
            , 'honeypot': honeypot
            , 'stored': stored
            , 'url': url
            , 'contextUrl': context_url
            , 'contextTitle': context_title}
        data = __cat_maybe_values(tuples)
        answer = __service('POST', 'content', data, )

        # for now, we check for a None, this should be fixed when we throw exceptions
        if answer == None:
            return None

        return self.__parseContentResponse(json.loads(answer))
