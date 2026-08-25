GitHub Include Directive Examples
==================================

Basic examples of the ``github-include`` directive.

Parse reStructuredText
----------------------

.. github-include:: sphinx-doc/sphinx:README.rst
   :branch: master
   :start-line: 21
   :end-line: 25

Parse Markdown (MyST)
---------------------

.. github-include:: psf/requests:README.md
   :start-line: 9
   :end-line: 28

Code with Syntax Highlighting
------------------------------

.. github-include:: python/cpython:Lib/this.py
   :code: python

Literal Text Display
--------------------

.. github-include:: github/gitignore:Python.gitignore
   :literal:
   :start-line: 1
   :end-line: 15
