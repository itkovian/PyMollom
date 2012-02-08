#
# (C) 2012, Andy Georges
#
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


    def createEntry(self):
        pass


    def updateEntry(self):
        pass


    def deleteEntry(self):
        pass


    def listEntries(self):
        pass


    def readEntry(self):
        pass


