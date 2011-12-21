# -*- coding: utf-8 -*-


class ImproperlyConfigured(Exception):
    pass


class Configuration(dict):
    @classmethod
    def from_module(cls, module, **defaults):
        defaults.update({k:v for k,v in module.__dict__.items() if k.upper() == k and not k.startswith('_')})
        return cls(defaults)
    
    @classmethod
    def from_configuration(cls, conf, key, **defaults):
        fullkey = '%s_' % key
        defaults.update({k[len(fullkey):]:v for k,v in conf.items() if k.startswith(fullkey)})
        conf = cls(defaults)
        conf.chain = [key]
    
    def get_sub_conf(self, key, **defaults):
        conf = Configuration.from_configuration(self, key, **defaults)
        for key in getattr(self, 'chain', []):
            conf.chain.insert(-1, key)
        return conf
    
    def ensure(self, *keys):
        chain = getattr(self, 'chain', [])
        if chain:
            chainstr = '_'.join(chain + [''])
            translate = lambda key: '%s_%s' % (chainstr, key)
        else:
            translate = lambda key: key
        for key in keys:
            if key not in self:
                raise ImproperlyConfigured("Configuration %r is required but not found" % translate(key))
