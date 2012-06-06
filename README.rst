========
PyMollom
========

A Python library for the `Mollom`_ anti-spam service.

A PyPI package is available at `PyPI_pymollom`_. This package still implements
the old XMLRPC API. Right now, the code base is moving towards the new REST API.


XMLRPC Example: ::

  from Mollom import MollomAPI
  from Mollom import MollomFault

  def content_is_spam(content):
      mollom_api = MollomAPI(
          publicKey=MOLLOM_PUBLIC_KEY,
          privateKey=MOLLOM_PRIVATE_KEY)
      if not mollom_api.verifyKey():
          raise MollomFault('Your MOLLOM credentials are invalid.')

      cc = mollom_api.checkContent(postBody=content)
      # cc['spam']: 1 for ham, 2 for spam, 3 for unsure;
      # http://mollom.com/blog/spam-vs-ham
      if cc['spam'] == 2:
          return True
      return False


.. _`Mollom`: http://mollom.com/
.. _`PyPI_pymollom`: http://pypi.python.org/pypi?:action=display&name=PyMollom&version=0.1
