#
# (C) 2012, Andy Georges
#
# This module contains the class file for the Mollom Captcha API
# ---------------------------------------------------------------------



class Type(object):
    IMAGE = "image"
    AUDIO = "audio"


class Captcha(object):

    def __init__(self):
        self.captchaId = None

    def createCaptcha(self):
        pass

    def verifyCaptcha(self):
        pass


