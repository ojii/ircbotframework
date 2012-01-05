# -*- coding: utf-8 -*-
from ircbotframework.utils import get_plugin_conf_key

class RegistryDictionary(dict):
    def __call__(self, name):
        def decorator(meth):
            self[name] = meth
            return meth
        return decorator


class BasePlugin(object):
    commands = RegistryDictionary()
    routes = RegistryDictionary()
    conf_key = None
    default_confs = None
    required_confs = None
    
    def __init__(self, protocol, conf):
        self.protocol = protocol
        self.conf = conf
        conf_key = self.conf_key or get_plugin_conf_key(self.__class__.__name__)
        defaults = self.default_confs or {}
        required = self.required_confs or ()
        self.plugin_conf = self.conf.get_sub_conf(conf_key, **defaults)
        self.plugin_conf.ensure(*required)
        self.post_init()
        
    # Internal
        
    def _handle_command(self, command, rest, channel, user):
        """
        INTERNAL
        """
        handler = self.commands.get(command, None)
        if handler is not None:
            handler(self, rest, channel, user)
    
    def _handle_http(self, request):
        """
        INTERNAL
        """
        for route, handler in self.routes.items():
            match = route.match(request.path)
            if match:
                kwargs = match.groupdict()
                if kwargs:
                    args = ()
                else:
                    args = match.groups()
                handler(self, request, *args, **kwargs)
                
    # Utility
    
    def message_channel(self, message):
        """
        Convenience function to message the default channel.
        """
        self.protocol.msg(self.protocol.factory.conf['CHANNEL'], message)

    # API
        
    def post_init(self):
        """
        Can be overwritten by subclasses if they want to do special stuff after
        init.
        """
        pass
    
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
    
    def handle_mention_message(self, message, channel, user):
        """
        If the bot gets mentioned (eg 'YourBot, how are you?' if 'YourBot' is
        the name of your bot. The message will not contain the bot name and the
        leading non-alphanumeric characters.
        """
        pass
