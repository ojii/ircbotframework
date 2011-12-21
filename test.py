# -*- coding: utf-8 -*-
"""
Run my test bot
"""

if __name__ == '__main__':
    from ircbotframework.main import run_with_settings_module
    import test_settings
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    run_with_settings_module(test_settings)
