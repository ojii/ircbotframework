# -*- coding: utf-8 -*-
"""
Test settings for test_plugins
"""

NETWORK = 'irc.freenode.net'
PORT = 6667
WEBHOOKS = True
WEBHOOK_PORT = 9999
CHANNEL = '#ircbotframeworktest'
NICKNAME = 'ircbotframeworktestbot'
PLUGINS = [
    'test_plugins.EchoPlugin',
    'test_plugins.WebhookPlugin',
    'test_plugins.CommandPlugin',
]
