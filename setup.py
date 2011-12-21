from setuptools import setup
from ircbotframework import __version__ as version
import os

README = os.path.join(os.path.dirname(__file__), 'README.rst')

with open(README) as fobj:
    long_description = fobj.read()

setup(name="ircbotframework",
    version=version,
    description="An IRC Bot framework for Python",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='irc twisted',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='http://github.com/ojii/ircbotframework',
    license='BSD',
    packages=['ircbotframework'],
    install_requires=['twisted'],
    zip_safe=False,
)
