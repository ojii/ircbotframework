# -*- coding: utf-8 -*-
from ircbotframework.bot import IRCBotFactory
from ircbotframework.http import HTTPServer
from twisted.internet import reactor


class Core(object):
    def __init__(self, network, ircport, channel, nickname, webport, app_classes, storage):
        self.network = network
        self.ircport = ircport
        self.channel = channel
        self.nickname = nickname
        self.webport = webport
        self.storage = storage
        self.apps = [app_class(self) for app_class in app_classes]
        self._irc_messages = []

    def run(self):
        self.irc = IRCBotFactory(self)
        reactor.connectTCP(self.network, self.ircport, self.irc)
        reactor.listenTCP(self.webport, HTTPServer(self))
        reactor.run()
    
    def message_channel(self, text):
        if getattr(self.irc.protocol_instance, 'is_connected', False):
            self.irc.protocol_instance.msg(self.channel, text)
        else:
            self._irc_messages.append((self.channel, text))
    
    def message_user(self, user, text):
        if getattr(self.irc.protocol_instance, 'is_connected', False):
            self.irc.protocol_instance.msg(user, text)
        else:
            self._irc_messages.append((user, text))
