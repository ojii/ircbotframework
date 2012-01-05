from ircbotframework.utils import load_object
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
        return self.factory.conf['NICKNAME']
    
    def set_nickname(self, val):
        self.factory.conf['NICKNAME'] = val
    nickname = property(get_nickname, set_nickname)

    def signedOn(self):
        """
        After the bot signed on to the server
        
        Join the channel and cache user perms.
        
        Load plugins
        
        Handle unhandled webhook requests
        """
        log.msg("IRCBot.signedOn")
        self.join(self.factory.conf['CHANNEL'])
        self.sendLine('NAMES %s' % self.factory.conf['CHANNEL'])
        self.plugins = []
        for import_path in self.factory.conf['PLUGINS']:
            klass = load_object(import_path)
            plugin = klass(self, self.factory.conf)
            self.plugins.append(plugin)
            log.msg("Loaded plugin %s" % plugin)
        while self.factory.unhandled_requests:
            request = self.factory.unhandled_requests.pop()
            self.handle_http(request)
        
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
        self.handle_joined(channel)

    def privmsg(self, rawuser, rawchannel, message):
        """
        When the bot receives a privmsg (from a user or channel)
        """
        log.msg("Handling privmsg %r %r %r" % (rawuser, rawchannel, message))
        channel = Channel(self, rawchannel)
        nick = rawuser.split('!')[0]
        mode = self.user_modes.get(nick, MODE_NORMAL)
        user = User(self, nick, mode)
        self.handle_message(message, channel, user)

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
                    
    def handle_message(self, message, channel, user):
        """
        Handles a single message
        
        Calls the plugin_message method on all plugins and if the message 
        starts with the command prefix, also calls handle_command.
        """
        raw_command = message[len(self.factory.conf['COMMAND_PREFIX']):]
        if ' ' in raw_command:
            command, rest = raw_command.split(' ', 1)
        else:
            command, rest = raw_command, ''
        is_mention = message.startswith(self.nickname)
        if is_mention:
            mention_message = message[len(self.nickname):].lstrip(NON_LETTERS)
        else:
            mention_message = ''
        for plugin in self.plugins:
            plugin.handle_message(message, channel, user)
            if command:
                plugin._handle_command(command, rest, channel, user)
            if is_mention:
                plugin.handle_mention(mention_message, channel, user)
    
    def handle_joined(self, channel):
        """
        Calls the handle_joined method on all plugins
        """
        for plugin in self.plugins:
            plugin.handle_joined(channel)
    
    def handle_http(self, request):
        """
        Handles a http request by calling each plugins handle_http method
        """
        for plugin in self.plugins:
            plugin._handle_http(request)
            

class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, conf):
        self.conf = conf
        self.unhandled_requests = []
        self.protocol_instance = None
        
    def buildProtocol(self, addr):
        self.protocol_instance = protocol.ClientFactory.buildProtocol(self, addr)
        return self.protocol_instance

    def clientConnectionLost(self, connector, reason):
        log.msg("IRCBotFactory.clientConnectionLost")
        connector.connect()
