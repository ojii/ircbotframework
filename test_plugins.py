# -*- coding: utf-8 -*-
"""
Some simple test plugins for me to check if stuff works or not
"""
from ircbotframework.plugin import BasePlugin, CommandsRegistry, RoutesRegistry
import re


class EchoPlugin(BasePlugin):
    def handle_message(self, message, channel, user):
        channel.msg("%s said %r in %r" % (user, message, channel))

class WebhookPlugin(BasePlugin):
    routes = RoutesRegistry()
    
    @routes(re.compile('^/$'))
    def root(self, request):
        self.message_channel("HTTP %r: %r" % (request.method, request.path))

class CommandPlugin(BasePlugin):
    commands = CommandsRegistry()
    
    @commands('test')
    def test_command(self, rest, channel, user):
        channel.msg("Got test command: %r" % rest)
