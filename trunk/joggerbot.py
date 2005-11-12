#! /usr/bin/env python
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

__revision__ = '$Id$'

import sys

import pyxmpp
from pyxmpp.jabberd.component import Component, ComponentError

class Bot(Component):
    
    def __init__(self, config):
        Component.__init__(self)
        self.cfg = config


if __name__ == '__main__':
    import config
    cfg = config.Config(sys.argv[1])
    try:
        joggerbot = Bot()
    finally:
        cfg.close()