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
# This module contains the class file for the Mollom Blacklist API
# ---------------------------------------------------------------------

from PyMollom import *
from Util import catMaybeValues


class BlacklistResponse(MollomResponse):
    """Responses obtained from the Blacklist API."""
    def __init__( self
                , id
                , create_timestamp
                , status
                , last_match
                , match_count
                , value
                , reason
                , context
                , match
                , note):
        """Initialise instance."""
        self.id = id
        self.create_timestamp = create_timestamp
        self.status = status
        self.last_match = last_match
        self.match_count = match_count
        self.value = value
        self.reason = reason
        self.context = context
        self.match = match
        self.note = note

    def fromJSON(self, js):
        """Convert a JSON string to the corresponding SiteResponse."""
        return BlacklistResponse( id=js.get('id')
                                , create_timestamp=int(js.get('created'))
                                , status=js.get('status')
                                , last_match=int(js.get('lastMatch'))
                                , match_count=int(js.get('matchCount'))
                                , value=js.get('value')
                                , reason=Reason.fromJSON(js.get('reason'))
                                , context=Context.fromJSON(js.get('context'))
                                , match=Match.fromJSON(js.get('match'))
                                , note=js.get('note'))


class Reason(object):
    SPAM = "spam"
    PROFANITY = "profanity"
    QUALITY = "quality"
    UNWANTED = "unwanted"

    def fromJSON(js):
        pass


class Context(object):
    ALL_FIELDS = "allFields"
    AUTHOR_IP = "authorIp"
    AUTHOR_ID = "authorId"
    AUTHOR_NAME = "authorName"
    AUTHOR_MAIL = "authorMail"
    LINKS = "links"
    POST_TITLE = "postTitle"

    def fromJSON(js):
        pass


class Match(object):
    EXACT = "exact"
    CONTAINS = "contains"

    def fromJSON(js):
        pass


class Blacklist(MollomBase):
    def __init__(self, public_key, private_key):
        super(MollomBase, self).__init__(public_key, private_key)

    def __decode(self, content):
        """Turn the JSON response into a BlacklistResponse."""
        return(BlacklistResponse().fromJSON(JSONDecoder().decode(content)['entry']))

    def create_entry( self
                    , value
                    , reason=Reason.UNWANTED
                    , context=Context.ALL_FIELDS
                    , match=Match.CONTAINS
                    , status=1
                    , note=None):
        """Create a new blacklist entry."""
        data = {
            'value': value,
            'reason': reason,
            'context': context,
            'match': match,
            'status': '%d' % (status)
        }
        if not note is None:
            data['note'] = Note
        path = "blacklist/{public_key}/".format(self.public_key)

        try:
            content = self.__service('POST', path, data)
            return self.__decode(content)
        except MollomError, _:
            raise

    def update_entry( self
                    , entry_id
                    , value=None
                    , reason=None
                    , context=None
                    , match=None
                    , status=None
                    , note=None):
        """Update a blacklist entry.

        @type entry_id: string representing a blacklist entry ID.
        @type value: string to blacklist.
        @type reason: Reason instance describing why the entry is blacklisted.
        @type context: Context instance describing the context of the blacklisting.
        @type match: Match instance describig how the entry should be matched.
        @type status: 0 or 1, stating if the entry is enabled or not.
        @type note: string representing additional information for the blacklisting.

        @returns: BlacklistResponse instance.

        @raise: MollomError is the entry cannot be updated.
        """
        data = catMaybeValues({
            'value': value,
            'reason': reason,
            'context': context,
            'match': match,
            'status': '%d' % (status)
            })
        path = "blacklist/{public_key}/{entry_id}".format(public_key=self.public_key, entry_id=entry_id)

        try:
            content = self.__service('POST', path, data)
            return self.__decode(content)
        except MollomError, m_err:
            raise

    def delete_entry( self
                    , entry_id):
        """Delete a blacklist entry.

        @type entry_id: string representing the blacklist entry ID.

        @raise MollomError if the entry cannot be deleted for some reason.
        """
        path = "blacklist/{public_key}/{entry_id}/delete".format(public_key=self.public_key, entry_id=entry_id)
        try:
            self.__service('POST', path, {})
            return True
        except MollomError, _:
            raise

    def list_entries(self):
        """List the entries in the blacklist.

        @returns: list of BlacklistResponse instances
        """
        path = "blacklist/{public+key}".format(public_key=self.public_key)
        try:
            entries = self.__service('GET', path, {})
            return map(lambda e: self.__decode(e), entries)
        except MollomError, _:
            raise


    def read_entry(self,
                   entry_id):
        """Read the information Mollom has about a blacklist entry.

        @type entry_id: string representing the blacklist entry ID.

        @returns: BlacklistResponse instance
        """
