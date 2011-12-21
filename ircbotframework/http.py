# -*- coding: utf-8 -*-
from twisted.web.resource import Resource


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
