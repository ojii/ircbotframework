# -*- coding: utf-8 -*-
"""
Some simple test plugins for me to check if stuff works or not
"""
from ircbotframework.plugin import BasePlugin


class EchoPlugin(BasePlugin):
    def handle_message(self, user, channel, message):
        channel.msg(message)

class WebhookPlugin(BasePlugin):
    def handle_http(self, request):
        self.message_channel("HTTP %r: %r" % (request.method, request.path))
