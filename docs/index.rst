.. Hurricane documentation master file, created by
   sphinx-quickstart on Wed Dec 16 22:09:01 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. image:: _static/img/logo.png
  :width: 400
  :alt: Alternative text
|
Hurricane is an initiative to fit `Django <https://www.djangoproject.com/>`_ perfectly with
`Kubernetes <https://kubernetes.io/>`_. It is supposed to cover many capabilities in order to run Django in a
cloud-native environment, including a `Tornado <https://www.tornadoweb.org/>`_-powered Django application server. It
was initially created by `Blueshoe GmbH <https://www.blueshoe.de/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   metrics
   todos

API Reference
-------------

Here you find detailed descriptions of specific functions and classes.

.. toctree::
   :maxdepth: 2

   api/management
   api/server
   api/metrics
   api/amqp
   api/webhooks

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
