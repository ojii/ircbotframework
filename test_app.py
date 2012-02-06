# -*- coding: utf-8 -*-
"""
Some simple test plugins for me to check if stuff works or not
"""
from ircbotframework.app import Application, View
from ircbotframework.plugin import Plugin



class TestView(View):
    def get(self, request):
        self.core.message_channel("Test View was GETed")
        return "OK"


class TestPlugin(Plugin):
    def get_commands(self):
        return [('!test', self.handle_test_command, "A test command")]
    
    def handle_test_command(self, message, channel, user):
        channel.msg("Test command called!")
    
    def handle_privatemessage(self, message, user):
        user.msg("I got a private message from you")
        
    def handle_message(self, message, channel, user):
        channel.msg("I got a message from you!")
    
    def handle_mention(self, message, channel, user):
        channel.msg("YAY I got noticed!")


class TestApplication(Application):
    def get_plugins(self):
        return [TestPlugin]
    
    def get_urls(self):
        return [
            ('/test/', TestView)
        ]
