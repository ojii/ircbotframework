# -*- coding: utf-8 -*-


class BasePlugin(object):
    def __init__(self, protocol, conf):
        self.protocol = protocol
        self.conf = conf
    
    def message_channel(self, message):
        """
        Convenience function to message the default channel.
        """
        self.protocol.msg(self.protocol.factory.conf['CHANNEL'], message)
        
    def handle_command(self, command, rest, channel, user):
        """
        Semi-internal API.
        
        You should implement a command_xyz method for all your commands,
        replacing xyz with your command name.
        """
        handler = getattr(self, 'command_%s' % command, None)
        if callable(handler):
            handler(rest, channel, user)

    def handle_message(self, message, channel, user):
        """
        Handle a single message sent to a channel by a user
        """
        pass
    
    def handle_joined(self, channel):
        """
        After the channel was joined
        """
        pass
    
    def handle_http(self, request):
        """
        Handle a HTTP request to the webhook
        """
        pass
