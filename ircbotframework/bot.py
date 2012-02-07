from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc
import string

MODE_NORMAL = 0
MODE_VOICE = 1
MODE_OPERATOR = 2

NON_LETTERS = string.whitespace + string.punctuation

class User(object):
    """
    Represents a user on IRC.
    """
    def __init__(self, client, nick, mode):
        self.client = client
        self.nick = nick
        self.mode = mode
        
    def __repr__(self):
        return '<User:%s>' % self.nick
        
    def __unicode__(self):
        return self.nick
    
    def msg(self, message):
        """
        Send this user a message
        """
        self.client.msg(self.nick, message)


class Channel(object):
    """
    Represents a channel on IRC
    """
    def __init__(self, client, name):
        self.client = client
        self.name = name
        
    def __repr__(self):
        return '<Channel:%s>' % self.name
        
    def __unicode__(self):
        return self.name
    
    def msg(self, message):
        """
        Send this channel a message
        """
        self.client.msg(self.name, message)


class IRCBot(irc.IRCClient):
    """
    The IRC bot protocol
    """
    def __init__(self):
        self.user_modes = {}

    # nickame property
    def get_nickname(self):
        return self.factory.core.nickname
    
    def set_nickname(self, val):
        self.factory.core.nickname = val
    nickname = property(get_nickname, set_nickname)

    def signedOn(self):
        """
        After the bot signed on to the server
        
        Join the channel and cache user perms.
        
        Load plugins
        
        Handle unhandled webhook requests
        """
        log.msg("IRCBot.signedOn")
        self.join(self.factory.core.channel)
        self.sendLine('NAMES %s' % self.factory.core.channel)
        self.plugins = []
        self.commands = {}
        self.command_help = {}
        # load all plugins and commands
        for app in self.factory.core.apps:
            # iterate over the plugins in an app
            for plugin_class in app.get_plugins():
                # instantiate the plugin bound to the core
                plugin = plugin_class(self.factory.core)
                self.plugins.append(plugin)
                # load all commands exposed by this plugin
                for commandname, handler, helptext in plugin.get_commands():
                    self.commands[commandname] = handler
                    self.command_help[commandname] = helptext
                log.msg("Loaded plugin %s" % plugin)
        # since we're connected now, handle all buffered messages (from webhooks)
        self.is_connected = True
        while self.factory.core._irc_messages:
            user, message = self.factory.core._irc_messages.pop(0)
            self.msg(user, message)
        
    def msg(self, user, message, length=None):
        """
        Send a message to a channel, enforces message encoding
        """
        encoded_message = unicode(message).encode('ascii', 'ignore')
        log.msg("Sending %r to %r" % (encoded_message, user))
        irc.IRCClient.msg(self, user, encoded_message, length)

    def joined(self, rawchannel):
        """
        After the bot joined a channel
        """
        log.msg("IRCBot.joined: %s" % rawchannel)
        channel = Channel(self, rawchannel)
        self.plugin_joined(channel)

    def privmsg(self, rawuser, rawchannel, message):
        """
        When the bot receives a privmsg (from a user or channel)
        """
        log.msg("Handling privmsg %r %r %r" % (rawuser, rawchannel, message))
        # check for private message
        nick = rawuser.split('!')[0]
        mode = self.user_modes.get(nick, MODE_NORMAL)
        user = User(self, nick, mode)
        if rawchannel == self.nickname:
            self.plugin_privatemessage(message, user)
        else:
            channel = Channel(self, rawchannel)
            self.plugin_message(message, channel, user)

    def irc_unknown(self, prefix, command, params):
        """
        Unknown (to twisted) IRC command, the response to the NAMES query we
        do in signedOn
        """
        log.msg("Handling unknown IRC command: %r %r %r" % (prefix, command, params))
        if command == 'RPL_NAMREPLY':
            self.handle_namereply(*params)

    def handle_namereply(self, myname, channeltype, channelname, users):
        """
        Handles a RPL_NAMREPLY command, caches user modes
        """
        for user in users.split(' '):
            if user.startswith('@'):
                nick = user[1:]
                self.user_modes[nick] = MODE_OPERATOR
            elif user.startswith('+'):
                nick = user[1:]
                self.user_modes[nick] = MODE_VOICE
            else:
                self.user_modes[user] = MODE_NORMAL
                
    def userRenamed(self, old, new):
        """
        When a user is renamed, re-cache permissions
        """
        log.msg("User renamed %r->%r" % (old, new))
        self.user_modes[new] = self.user_modes.pop(old, MODE_NORMAL)
    
    def userLeft(self, user, channel):
        """
        When a user leaves a channel, remove user mode cache
        """
        nick = user.split('!')[0]
        log.msg("User left %r" % nick)
        self.user_modes.pop(nick, None)
    
    def modeChanged(self, user, channel, set_mode, modes, args):
        """
        When a user mode changes, re-cache permissions
        """
        log.msg("Mode changed: %r %r %r %r %r" % (user, channel, set_mode, modes, args))
        nick = args[0] if len(args) == 1 else None
        if 'o' in modes:
            if set_mode:
                self.user_modes[nick] = MODE_OPERATOR
            elif not set_mode:
                self.user_modes[nick] = MODE_NORMAL
        elif 'v' in modes:
            if set_mode:
                self.user_modes[nick] = MODE_VOICE
            elif not set_mode:
                self.user_modes[nick] = MODE_NORMAL
                
    # API proxies
                    
    def plugin_message(self, message, channel, user):
        """
        Handles a single message
        
        Calls the plugin_message method on all plugins and if the message 
        starts with the command prefix, also calls handle_command.
        """
        bits = message.split(' ')
        command = bits[0] if bits else None
        log.msg("Command is %s" % command)
        if command is not None:
            if command in self.commands:
                # call the command
                log.msg("Command found, calling...")
                self.commands[command](message, channel, user)

        # check if this is a mention
        is_mention = message.startswith(self.nickname)
        if is_mention:
            mention_message = message[len(self.nickname):].lstrip(NON_LETTERS)
            log.msg("It's a mention of me!")
        else:
            mention_message = ''
        for plugin in self.plugins:
            plugin.handle_message(message, channel, user)
            if is_mention:
                plugin.handle_mention(mention_message, channel, user)
                    
    def plugin_privatemessage(self, message, user):
        """
        Handles a single private message
        """
        bits = message.split(' ')
        command = bits[0] if bits else None
        if command is not None:
            if command in self.commands:
                # call the command
                self.commands[command](message, user, user)

        for plugin in self.plugins:
            plugin.handle_privatemessage(message, user)
    
    def plugin_joined(self, channel):
        """
        Calls the handle_joined method on all plugins
        """
        for plugin in self.plugins:
            plugin.handle_joined(channel)


class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, core):
        self.core = core
        self.protocol_instance = None
        
    def buildProtocol(self, addr):
        self.protocol_instance = protocol.ClientFactory.buildProtocol(self, addr)
        return self.protocol_instance

    def clientConnectionLost(self, connector, reason):
        log.msg("IRCBotFactory.clientConnectionLost")
        connector.connect()
