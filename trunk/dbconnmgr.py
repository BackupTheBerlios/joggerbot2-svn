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

"""Database connection manager."""

__revision__ = '$Id$'

import time

class DbConnectionManager:
    """Generic connection manager. This class defines only interface and few
    basic functionalities."""
    
    def __init__(self, config, logger):
        self.cfg = config
        self.logger = logger
        self.cn = None
    
    def tryConnect():
        """Generic method that attempts to establish connection to database.
        After succesful attempt a connection object would be returned, or 
        None if the attempt fails."""
        raise NotImplementedError

    def getConnection(self):
        """Returns connection object. If 
        """
        if not self.cn.connected():
            self.logger.warning('Connection to database lost, '
                'attempting to reconnect...')
            i = 0
            while i < 10:
                i = i + 1
                self.cn = self.tryConnect()
                if self.cn:
                    return self.cn
                else:
                    time.sleep(1)
