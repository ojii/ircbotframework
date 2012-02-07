# -*- coding: utf-8 -*-
from argparse import Namespace


class NULL: pass


class Argument(object):
    def __init__(self, name, default=NULL):
        self.name = name
        self.default = default
        self.required = default is NULL
    
    def get_usage(self):
        if self.required:
            return self.name
        else:
            return '[%s]' % self.name


class Command(object):
    def __init__(self, name, handler, help_text, *arguments):
        self.name = name
        self.handler = handler
        self.help_text = help_text
        self.arguments = arguments
    
    def get_usage(self):
        return "%s %s" % (self.name, ' '.join([argument.get_usage() for argument in self.arguments]))
    
    def handle(self, bits, channel, user):
        namespace = Namespace()
        for argument in self.arguments:
            if bits:
                bit = bits.pop(0)
            else:
                bit = None
            if bit:
                setattr(namespace, argument.name, bit)
            elif argument.required:
                channel.msg("Required argument %r not given. %r usage is: %s" % (argument.name, self.name, self.get_usage()))
                return
            else:
                setattr(namespace, argument.name, argument.default)
        self.handler(namespace, channel, user)
