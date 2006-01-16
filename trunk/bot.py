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

import platform, sys, time, signal

if sys.platform == 'win32':
    from pysqlite2 import dbapi2 as db
else:
    import MySQLdb as db

import pyxmpp
from pyxmpp.all import JID, Presence
from pyxmpp.jabberd.component import Component, ComponentError

class Bot(Component):
    
    def __init__(self, config, logger):
        """Create instance and initialize from configuration options.
        Also set logger to global default one."""
        self.serverOpts = config.getOptions('server')
        self.mysqlOpts = config.getOptions('mysql')
        self.compOpts = config.getOptions('component')
        # initialize component
        logger.info('JoggerBot component initializing')
        name = self.compOpts['name']
        secret = self.serverOpts['secret']
        serverHostname = self.serverOpts['hostname']
        port = int(self.serverOpts['port'])
        try:
            fullName = self.compOpts['fullname']
        except KeyError:
            # using old configuration data
            self.logger.warning('Old configuration data is used')
            fullName = name
        Component.__init__(self, JID(name), secret, serverHostname, port,
            disco_name=fullName, disco_category='x-service',
            disco_type='x-jogger')
        self.disco_info.add_feature('jabber:iq:version')
        logger.info('JoggerBot component initialized')
        self.startTime = time.time()
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
        self._connectDB()

    ### internal service methods ###
    def _connectDB(self):
        self.logger.info('Connecting to database...')
        if sys.platform == 'win32':
            self.dbConn = db.connect('joggerbot.db')
        else:
            host = self.mysqlOpts['server']
            user = self.mysqlOpts['username']
            passwd = self.mysqlOpts['password']
            dbName = self.mysqlOpts['dbname']
            self.dbConn = db.connect(host, user, passwd, dbName)
        self.logger.info('JoggerBot connected to its database')

    def stream_state_changed(self, state, arg):
        self.logger.debug('State changed: %s %r' % (state, arg))

    ### event handlers ###
    def authenticated(self):
        self.logger.info('Trying to authenticate with server...')
        Component.authenticated(self)
        self.logger.info('JoggerBot component authenticated')
        # set up handlers for supported <iq/> queries
        self.stream.set_iq_get_handler('query', 'jabber:iq:version', self.getVersionQuery)
        self.stream.set_iq_get_handler('query', 'jabber:iq:register', self.getRegisterQuery)
        self.stream.set_iq_set_handler('query', 'jabber:iq:register', self.setRegisterQuery)
        self.stream.set_iq_get_handler('query', 'jabber:iq:last', self.onLastQuery)        
        # set up handlers for <presence/> stanzas
        self.stream.set_presence_handler('probe', self.onProbe)
        self.stream.set_presence_handler('available', self.onPresence)
        self.stream.set_presence_handler('subscribe', self.onSubscriptionChange)
        self.stream.set_presence_handler('unsubscribe', self.onSubscriptionChange)
        # set up handler for <message stanza>
        self.stream.set_message_handler('normal', self.onMessage)
    
    def disconnected(self):
        self.logger.warning('Connection to XMPP/Jabber server %s has been lost' % self.serverOpts['hostname'])
        try:
            attempts = int(self.serverOpts['attempts'])
        except KeyError:
            # using old configuration data
            self.logger.warning('Old configuration data is used')
            attempts = 20
        for i in range(attempts):
            time.sleep(30)
            self.logger.info('Attempting to reconnect (%d/%d)' % (i+1, attempts))
            self.connect()
            if self.stream:
                self.logger.info('Connection has been re-established')
                break
            else:
                self.logger.error('Unable to re-establish connection to XMPP/Jabber server %s' % self.serverOpts['hostname'])
        if not self.stream:
            self.logger.critical('Unable to establish connection to server, exiting')
            self.exit()

    ### stanza handlers ###
    def getVersionQuery(self, stanza):
        stanza = stanza.make_result_response()
        q = stanza.new_query('jabber:iq:version')
        q.newTextChild(q.ns(), 'name', 'Jogger.pl bot')
        q.newTextChild(q.ns(), 'version', '2.0')
        osData = platform.uname()
        if osData[0].lower() == 'windows':
            osName = osData[0] + ' '.join(platform.win32_ver())
        else:
            osName = ' '.join(osData)
        q.newTextChild(q.ns(), 'os', osName)
        self.stream.send(stanza)
        return True
    
    def getRegisterQuery(self, stanza):
        pass
    
    def setRegisterQuery(self, stanza):
        pass
    
    def onLastQuery(self, stanza):
        stanza = stanza.make_result_response()
        q = stanza.new_query('jabber:iq:last')
        q.newTextChild(q.ns(), 'seconds', str(time.time() - self.startTime))
        self.stream.send(stanza)
        return True
    
    def onPresence(self, stanza):
        self.logger.debug('Got presence data %s' % stanza.serialize())
        p = Presence(
            stanza_type = stanza.get_type(),
            to_jid = stanza.get_from(),
            from_jid = stanza.get_to(),
            show = None
        )
        self.stream.send(p)
    
    def onSubscriptionChange(self, stanza):
        p = stanza.make_accept_response()
        self.stream.send(p)
        fromUser = stanza.get_from().as_utf8()
        msg = None
        stanzaType = stanza.get_type()
        self.logger.debug('Got stanza %s from %s' % (stanzaType, fromUser))
        if stanza.get_type() == 'subscribe':
            msg = 'User %s subscribed' % fromUser
        elif stanza.get_type() == 'unsubscribe':
            msg = 'User %s unsubscribed' % fromUser
        if msg:
            self.logger.info(msg)
        return True
    
    def onProbe(self, stanza):
        p = Presence(
            stanza_type = stanza.get_type(),
            to_jid = stanza.get_from(),
            from_jid = stanza.get_to(),
            show = None
        )
        self.stream.send(p)
    
    def onMessage(self, stanza):
        toJid = stanza.get_to()
        toUser = toJid.node
        toResource = toJid.resource
        self.logger.debug('Got message to %s and resource %s' % (toUser, toResource))
        
    def exit(self):
        if self.stream:
            self.logger.info('Disconnecting from XMPP/Jabber server %s...' % \
                self.serverOpts['hostname'])
            self.disconnect()
        self.logger.info('Disconnecting from database server %s...' % \
            self.mysqlOpts['server'])
        self.cfg.close()
        sys.exit(0)

    def shutdown(self, sigNum, frame):
        self.exit()
