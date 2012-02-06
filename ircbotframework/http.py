# -*- coding: utf-8 -*-
from flask import Flask
from twisted.internet import reactor
from twisted.python.threadpool import ThreadPool
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource


class Webhook(Resource):
    is_leaf = True
    def __init__(self, irc_factory, conf):
        self.irc_factory = irc_factory
        self.conf = conf
        Resource.__init__(self)
        
    def getChildWithDefault(self, path, request):
        return self
    
    def render(self, request):
        self.proxy_to_irc(request)
        return self.conf['WEBHOOK_RESPONSE']
        
    def proxy_to_irc(self, request):
        protocol = self.irc_factory.protocol_instance
        if hasattr(protocol, 'plugins'):
            protocol.handle_http(request)
        else:
            self.irc_factory.unhandled_requests.append(request)


def get_flask_application(core):
    application = Flask(__name__)
    application.debug = True
    for app in core.apps:
        for url, view in app.get_urls():
            application.add_url_rule(url, view.__class__.__name__, view(core))
    return application


class HTTPServer(Site):
    def __init__(self, core):
        thread_pool = ThreadPool()
        thread_pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
        application = get_flask_application(core)
        wsgi_resource = WSGIResource(reactor, thread_pool, application)
        Site.__init__(self, wsgi_resource)
