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
import logging
from optparse import OptionParser

def parseCmdline():
    parser = OptionParser()
    parser.add_option('-c', '--config-file', dest='configFile',
        help='Configuration file name')
    options, args = parser.parse_args()
    if options.configFile is None:
        parser.print_help()
        sys.exit('Not enough command line arguments')
    return options

if __name__ == '__main__':
    import config, bot
    opts = parseCmdline()
    cfg = config.Config(opts.configFile)    
    logger = logging.getLogger('joggerbot')
    logHandler = logging.FileHandler(cfg.getOption('debug', 'file'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    joggerbot = bot.Bot(cfg, logger)
    #joggerbot.loop()