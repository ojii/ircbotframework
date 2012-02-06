# -*- coding: utf-8 -*-


class Plugin(object):
    def __init__(self, core):
        self.core = core
        
    def get_commands(self):
        """
        Returns a tuple of (commandname, handler, helptext)
        
        Handler will be called the same way as handle_message
        """
        return []
    
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
    
    def handle_mention(self, message, channel, user):
        """
        If the bot gets mentioned (eg 'YourBot, how are you?' if 'YourBot' is
        the name of your bot. The message will not contain the bot name and the
        leading non-alphanumeric characters.
        """
        pass
    
    def handle_privatemessage(self, message, user):
        """
        If the bot gets a private message.
        """
        pass
