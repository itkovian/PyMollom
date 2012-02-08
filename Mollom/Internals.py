#
# (C) 2012, Andy Georges
#
# This module contains the internal classes and code file for Mollom
# ---------------------------------------------------------------------

import oauth2
import urllib


def __service(method, path, data, maxRetries = 0, depth=0):
   """The service method makes the actual call to the Mollom service
   on behalf of the public API method.

   Returns:
     The result of the call, if a server is available.
     None after MOLLOM_RETRIES successive failed retries.
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
   consumer = oauth2.Consumer(key = self.publicKey, secret = self.privateKey)
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
