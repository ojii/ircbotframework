# -*- coding: utf-8 -*-
from flask import request

class View(object):
    def __init__(self, core):
        self.core = core
    
    def __call__(self, *args, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)
        if callable(handler):
            return handler(request=request, *args, **kwargs)
        else:
            return "Bad Request", 403


class Application(object):
    def __init__(self, core):
        self.core = core
    
    def get_urls(self):
        """
        Returns a list of tuples: (route, View)
        """
        return []
    
    def get_plugins(self):
        """
        Returns a list of plugin classes
        """
        return []
