# -*- coding: utf-8 -*-

# This file is part of Joggerbot, a JoggerPL-2.0 bot.
#
# Copyright: (c) 2005, Jarek Zgoda <jzgoda@o2.pl>
#
# Joggerbot is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation; either version 2 of the License, or (at your opinion) 
# any later version.
#
# Joggerbot is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License along with
# Joggerbot; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Main joggerbot component code."""

__revision__ = '$Id$'

import sys
import signal

import pyxmpp
from pyxmpp.all import JID
from pyxmpp.jabberd.component import Component, ComponentError

class Bot(Component):
    
    def __init__(self, config, logger):
        """Create instance and initialize from configuration options.
        Also set logger to global default one."""
        self.serverOpts = config.getOptions('server')
        self.mysqlOpts = config.getOptions('mysql')
        self.compOpts = config.getOptions('component')
        # initialize component
        Component.__init__(self, 
            jid=JID(self.compOpts['name']),
            secret=self.serverOpts['secret'],
            server=self.serverOpts['hostname'],
            port=int(self.serverOpts['port']),
            disco_name=self.compOpts['name'],
            disco_category='x-service')
        self.disco_info.add_feature('jabber:iq:version')
        logger.info('JoggerBot initializing...')
        self.cfg = config
        self.logger = logger
        # the signals we should respond to with graceful exit
        # for debug purpose also check Win platform
        if sys.platform == 'win32':
            signals = (signal.SIGTERM, signal.SIGINT)
        else:
            signals = (signal.SIGHUP, signal.SIGKILL, 
                signal.SIGTERM, signal.SIGINT)
        for sign in signals:
            signal.signal(sign, self.shutdown)
        self._connectServer()
        self._connectDB()

    ### internal service methods ###
    def _connectServer(self):
        pass
    
    def _connectDB(self):
        pass

    ### event handlers ###
    def authenticated(self):
        Component.authenticated(self)
        # set up handlers for supported <iq/> queries
        self.stream.set_iq_get_handler('query', 'jabber:iq:version', self.getVersionQuery)
        self.stream.set_iq_get_handler('query', 'jabber:iq:register', self.getRegisterQuery)
        self.stream.set_iq_set_handler('query', 'jabber:iq:register', self.setRegisterQuery)
        self.stream.set_iq_get_handler('query', 'jabber:iq:last', self.onLastQuery)        
        # set up handlers for <presence/> stanzas
        self.stream.set_presence_handler('available', self.onPresence)
        self.stream.set_presence_handler('subscribe', self.onSubscribe)
        self.stream.set_presence_handler('unsubscribe', self.onUnsubscribe)
        # set up handler for <message stanza>
        self.stream.set_message_handler('normal', self.onMessage)

    ### stanza handlers ###
    def getVersionQuery(self, stanza):
        pass

    def shutdown(self, sigNum, frame):
        self.logger.info('Disconnecting from XMPP/Jabber server %s...' % \
            self.serverOpts['hostname'])
        self.disconnect()
        self.logger.info('Disconnecting from MySQL server %s...' % \
            self.mysqlOpts['server'])
        self.cfg.close()
        sys.exit(0)

