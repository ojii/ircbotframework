# -*- coding: utf-8 -*-
from importlib import import_module
from ircbotframework.bot import IRCBotFactory
from ircbotframework.conf import Configuration
from ircbotframework.http import Webhook
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
import sys

def run(conf):
    conf.ensure('NETWORK', 'PORT', 'CHANNEL', 'NICKNAME', 'COMMAND_PREFIX')
    if conf['WEBHOOKS']:
        conf.ensure('WEBHOOK_PORT')
    irc = IRCBotFactory(conf)
    reactor.connectTCP(conf['NETWORK'], conf['PORT'], irc)
    if conf['WEBHOOKS']:
        webhook = Webhook(irc, conf)
        reactor.listenTCP(conf['WEBHOOK_PORT'], Site(webhook))
        pass
    reactor.run()

def run_with_settings_module(module):
    conf = Configuration.from_module(module,
        WEBHOOKS=False,
        PLUGINS=[],
        COMMAND_PREFIX='!',
        WEBHOOK_RESPONSE='ok\n',
    )
    run(conf)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()
    if args.verbose:
        log.startLogging(sys.stdout)
    module = import_module(args.settings)
    run_with_settings_module(module)

if __name__ == '__main__':
    main()
