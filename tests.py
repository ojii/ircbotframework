# -*- coding: utf-8 -*-
from ircbotframework.conf import Configuration, ImproperlyConfigured
from ircbotframework.http import Webhook
from ircbotframework.main import run_with_settings_module
from ircbotframework.plugin import BasePlugin, RoutesRegistry
from ircbotframework.utils import load_object, get_plugin_conf_key
from twisted.internet import reactor
from twisted.trial import unittest as twistedtest
from twisted.web.client import getPage
from twisted.web.server import Site
import re
import unittest


class ConfTests(unittest.TestCase):
    def test_simple_conf(self):
        conf = Configuration({'KEY': 'value', 'SUB_KEY': 'sub value'})
        self.assertEqual(conf['KEY'], 'value')
        self.assertEqual(conf['SUB_KEY'], 'sub value')
        
    def test_subconf(self):
        conf = Configuration({'KEY': 'value', 'SUB_KEY': 'sub value'})
        subconf = conf.get_sub_conf('SUB')
        self.assertEqual(subconf['KEY'], 'sub value')
        
    def test_sub_sub_conf(self):
        conf = Configuration({'KEY': 'value', 'SUB_KEY': 'sub value', 'SUB_SUB_KEY': 'sub sub value'})
        subsubconf = conf.get_sub_conf('SUB').get_sub_conf('SUB')
        self.assertEqual(subsubconf['KEY'], 'sub sub value')
        
    def test_ensure_simple(self):
        conf = Configuration({'KEY': 'value'})
        self.assertEqual(conf.ensure('KEY'), None)
    
    def test_ensure_fails(self):
        conf = Configuration()
        with self.assertRaises(ImproperlyConfigured):
            conf.ensure('KEY')
    
    def test_ensure_fails_chaind(self):
        conf = Configuration({'KEY': 'value', 'SUB_KEY': 'sub value'})
        subconf = conf.get_sub_conf('SUB')
        with self.assertRaisesRegexp(ImproperlyConfigured, "SUB_SUB_KEY"):
            subconf.ensure('SUB_KEY')
    
    def test_from_module(self):
        mock_module = type('Module', (object,), {'KEY': 'value'})
        conf = Configuration.from_module(mock_module)
        self.assertEqual(conf['KEY'], 'value')


class UtilsTests(unittest.TestCase):
    def test_load_object(self):
        baseplugin = load_object('ircbotframework.plugin.BasePlugin')
        self.assertTrue(baseplugin is BasePlugin)
        
    def test_load_object_fails(self):
        with self.assertRaises(TypeError):
            load_object('fail')
    
    def test_get_plugin_conf_key(self):
        self.assertEqual(get_plugin_conf_key('Test'), 'TEST')
        self.assertEqual(get_plugin_conf_key('TestTwo'), 'TEST_TWO')


class WebhookTests(twistedtest.TestCase):
    def setUp(self):
        self.irc_mock = type('MockFactory', (object,), {'protocol_instance': None, 'unhandled_requests': []})
        self.webhook_response = 'test'
        webhook = Webhook(self.irc_mock, Configuration({'WEBHOOK_RESPONSE': self.webhook_response}))
        factory = Site(webhook)
        self.port = reactor.listenTCP(0, factory, interface="127.0.0.1")
        self.portnum = self.port.getHost().port
        
    def tearDown(self):
        port, self.port = self.port, None
        return port.stopListening()
        
    def test_simple(self):
        deferred = getPage('http://127.0.0.1:%s/' % self.portnum)
        def do_test(response):
            self.assertEqual(response, self.webhook_response)
        deferred.addCallback(do_test)
        return deferred
    
    def test_irc_already_connected(self):
        class PluginMock(BasePlugin):
            routes = RoutesRegistry()
            def __init__(self):
                self.requests = []
            
            @routes(re.compile(r'.*'))
            def handle(self, request):
                self.requests.append(request)
        mock_plugin = PluginMock()
        class MockProtocol(object):
            plugins = [mock_plugin]
            def handle_http(self, request):
                mock_plugin._handle_http(request)
        self.irc_mock.protocol_instance = MockProtocol()
        deferred = getPage('http://127.0.0.1:%s/' % self.portnum)
        def do_test(response):
            self.assertEqual(len(mock_plugin.requests), 1)
        deferred.addCallback(do_test)
        return deferred


if __name__ == '__main__':
    unittest.main()
