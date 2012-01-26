"""Setup script for PyMollom"""
from distutils.core import setup

setup(name='PyMollom',
      version='0.1',
      license='GPL',
      py_modules=['Mollom', 'HTTPTransport'],
      description='A Python library for the Mollom anti-spam service',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Topic :: Text Processing :: Filters',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ],
      )
