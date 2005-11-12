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

"""JoggerBot configuration handling."""

__revision__ = '$Id$'

from xml.dom import Node
import xml.dom.minidom

class Config:
    """Handle legacy joggerbot XML-based configuration.
    That's why XML configuration is stupid idea."""
    
    def __init__(self, fileName):
        """Load configuration from specified file."""
        self.dom = xml.dom.minidom.parse(fileName)

    def _getText(self, nodes):
        """Get content from all text nodes from nodeList or other iterable."""
        text = ''
        for node in nodes:
            if node.nodeType == Node.TEXT_NODE:
                text = text + node.data
        return text.strip()

    def getOption(self, section, option, default=None):
        """Get specified option value. Return default, if it does not exist."""
        ret = default
        options = self.dom.getElementsByTagName(section)[0].childNodes
        for optionNode in options:
            if optionNode.localName == option and \
                    optionNode.nodeType == Node.ELEMENT_NODE:
                ret = self._getText(optionNode.childNodes)
        return ret

    def close(self):
        """Defensive, as some Python implementations have problems with
        cleaning DOM memory."""
        self.dom.unlink()