# -*- coding: utf-8 -*-
"""
Run my test bot
"""
from test_app import TestApplication

if __name__ == '__main__':
    from ircbotframework.core import Core
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    core = Core('irc.freenode.net', 6667, '#botcloud-test', 'BotCloudTestBot', 5555, [TestApplication], {})
    core.run()
