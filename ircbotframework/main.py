# -*- coding: utf-8 -*-
from importlib import import_module
from ircbotframework.bot import IRCBotFactory
from ircbotframework.conf import Configuration
from ircbotframework.http import Webhook
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
import argparse
import os
import sys

def run(conf): # pragma: no cover
    conf.ensure('NETWORK', 'PORT', 'CHANNEL', 'NICKNAME', 'COMMAND_PREFIX',
                'WEBHOOKS', 'APPS')
    if conf['WEBHOOKS']:
        conf.ensure('WEBHOOK_PORT')
    irc = IRCBotFactory(conf)
    reactor.connectTCP(conf['NETWORK'], conf['PORT'], irc)
    if conf['WEBHOOKS']:
        webhook = Webhook(irc, conf)
        reactor.listenTCP(conf['WEBHOOK_PORT'], Site(webhook))
        pass
    reactor.run()

def run_with_settings_module(module): # pragma: no cover
    conf = Configuration.from_module(module,
        WEBHOOKS=False,
        PLUGINS=[],
        COMMAND_PREFIX='!',
        WEBHOOK_RESPONSE='ok\n',
    )
    run(conf)

def main(): # pragma: no cover
    sys.path.insert(0, os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument('settings')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()
    if args.verbose:
        log.startLogging(sys.stdout)
    module = import_module(args.settings)
    run_with_settings_module(module)

if __name__ == '__main__': # pragma: no cover
    main()
