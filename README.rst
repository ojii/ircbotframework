###############################
An IRC Bot framework for Python
###############################

************
Installation
************

Develop version
===============

``pip install -e git+git://github.com/ojii/ircbotframework.git#egg=ircbotframework``


***
Run
***

``ircbotframework <path.to.settings>``

Replace ``<path.to.settings>`` with a path to a settings file.

Add the ``--verbose`` flag if you want to enable logging (to stdout).


********
Settings
********

Required
========

``NETWORK``
-----------

The IRC network to connect to (string).

``PORT``
--------

The port the IRC network is running on (int).

``CHANNEL``
-----------

The channel to join (including the ``'#'``) (string).

``NICKNAME``
------------

The nickname of the bot (string).

``PLUGINS``
-----------

A list of strings pointing to plugin classes. Plugins must be subclasses of
``ircbotframework.plugin.BasePlugin``.


Optional
========

``COMMAND_PREFIX``
------------------

Prefix for commands, default ``'!'`` (string).

``WEBHOOKS``
------------

Whether to enable webhooks or not, default ``False`` (boolean).

``WEBHOOK_PORT``
----------------

If ``WEBHOOKS`` is ``True``, must be set. Port to listen for HTTP requests.


*******
Plugins
*******

Plugins are Python classes subclassing ``ircbotframework.plugin.BasePlugin``.
