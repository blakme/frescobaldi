# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Session menu.
"""

from __future__ import unicode_literals

from PyQt4.QtGui import QMenu

import app
from . import manager


class SessionMenu(QMenu):
    def __init__(self, mainwindow):
        super(SessionMenu, self).__init__(mainwindow)
        app.translateUI(self)
        ac = manager.get(mainwindow).actionCollection
        self.addAction(ac.session_new)
        self.addAction(ac.session_save)
        self.addSeparator()
        self.addAction(ac.session_manage)
        self.addSeparator()
        self.addAction(ac.session_none)
        self.addSeparator()
        self.aboutToShow.connect(self.populate)
    
    def translateUI(self):
        self.setTitle(_('menu title', '&Session'))
    
    def populate(self):
        manager.get(self.parentWidget()).populateSessionMenu(self)


