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
class Reason(object):
    SPAM = "spam"
    PROFANITY = "profanity"
    QUALITY = "quality"
    UNWANTED = "unwanted"


class Context(object):
    ALL_FIELDS = "allFields"
    AUTHOR_IP = "authorIp"
    AUTHOR_ID = "authorId"
    AUTHOR_NAME = "authorName"
    AUTHOR_MAIL = "authorMail"
    LINKS = "links"
    POST_TITLE = "postTitle"


class Match(object):
    EXACT = "exact"
    CONTAINS = "contains"


class Blacklist(object):
    def __init__(self):
        pass


    def create_entry(self):
        pass


    def update_entry(self):
        pass


    def delete_entry(self):
        pass


    def list_entries(self):
        pass


    def read_entry(self):
        pass


