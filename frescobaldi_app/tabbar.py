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
The tab bar with the documents.
"""

from __future__ import unicode_literals

import weakref

from PyQt4.QtCore import Qt, QUrl, pyqtSignal
from PyQt4.QtGui import QMenu, QTabBar

import app
import icons
import document
import jobmanager


class TabBar(QTabBar):
    """The tabbar above the editor window."""
    
    currentDocumentChanged = pyqtSignal(document.Document)
    
    def __init__(self, parent=None):
        super(TabBar, self).__init__(parent)
        
        self.setFocusPolicy(Qt.NoFocus)
        self.setTabsClosable(True) # TODO: make configurable
        self.setMovable(True)      # TODO: make configurable
        self.setExpanding(False)
        
        mainwin = self.window()
        self.docs = []
        for doc in app.documents:
            self.addDocument(doc)
            if doc is mainwin.currentDocument():
                self.setCurrentDocument(doc)
        
        app.documentCreated.connect(self.addDocument)
        app.documentClosed.connect(self.removeDocument)
        app.documentUrlChanged.connect(self.setDocumentStatus)
        app.documentModificationChanged.connect(self.setDocumentStatus)
        app.jobStarted.connect(self.setDocumentStatus)
        app.jobFinished.connect(self.setDocumentStatus)
        mainwin.currentDocumentChanged.connect(self.setCurrentDocument)
        self.currentChanged.connect(self.slotCurrentChanged)
        self.tabMoved.connect(self.slotTabMoved)
        self.tabCloseRequested.connect(self.slotTabCloseRequested)
        
    def documents(self):
        return list(self.docs)
        
    def addDocument(self, doc):
        if doc not in self.docs:
            self.docs.append(doc)
            self.blockSignals(True)
            self.addTab('')
            self.blockSignals(False)
            self.setDocumentStatus(doc)

    def removeDocument(self, doc):
        if doc in self.docs:
            index = self.docs.index(doc)
            self.docs.remove(doc)
            self.blockSignals(True)
            self.removeTab(index)
            self.blockSignals(False)

    def setDocumentStatus(self, doc):
        if doc in self.docs:
            index = self.docs.index(doc)
            self.setTabText(index, doc.documentName())
            tooltip = None
            if not doc.url().isEmpty():
                tooltip = doc.url().toString(QUrl.RemoveUserInfo)
            self.setTabToolTip(index, tooltip)
            # icon
            if jobmanager.isRunning(doc):
                icon = 'lilypond-run'
            elif doc.isModified():
                icon = 'document-save'
            else:
                icon = 'text-plain'
            self.setTabIcon(index, icons.get(icon))
    
    def setCurrentDocument(self, doc):
        """ Raise the tab belonging to this document."""
        if doc in self.docs:
            index = self.docs.index(doc)
            self.blockSignals(True)
            self.setCurrentIndex(index)
            self.blockSignals(False)

    def slotCurrentChanged(self, index):
        """ Called when the user clicks a tab. """
        self.currentDocumentChanged.emit(self.docs[index])
    
    def slotTabCloseRequested(self, index):
        """ Called when the user clicks the close button. """
        self.window().closeDocument(self.docs[index])
    
    def slotTabMoved(self, index_from, index_to):
        """ Called when the user moved a tab. """
        doc = self.docs.pop(index_from)
        self.docs.insert(index_to, doc)
        
    def nextDocument(self):
        """ Switches to the next document. """
        index = self.currentIndex() + 1
        if index == self.count():
            index = 0
        self.setCurrentIndex(index)
        
    def previousDocument(self):
        index = self.currentIndex() - 1
        if index < 0:
            index = self.count() - 1
        self.setCurrentIndex(index)
    
    def contextMenuEvent(self, ev):
        index = self.tabAt(ev.pos())
        if index >= 0:
            self.contextMenu().exec_(self.docs[index], ev.globalPos())

    def contextMenu(self):
        try:
            return self._contextMenu
        except AttributeError:
            self._contextMenu = TabContextMenu(self)
        return self._contextMenu


class TabContextMenu(QMenu):
    def __init__(self, parent):
        super(TabContextMenu, self).__init__(parent)
        self._doc = lambda: None
        self.doc_save = self.addAction(icons.get('document-save'), '')
        self.doc_save_as = self.addAction(icons.get('document-save-as'), '')
        self.addSeparator()
        self.doc_close = self.addAction(icons.get('document-close'), '')
        
        self.doc_save.triggered.connect(self.docSave)
        self.doc_save_as.triggered.connect(self.docSaveAs)
        self.doc_close.triggered.connect(self.docClose)
        app.languageChanged.connect(self.translateUI)
        self.translateUI()
    
    def translateUI(self):
        self.doc_save.setText(_("&Save"))
        self.doc_save_as.setText(_("Save &As..."))
        self.doc_close.setText(_("&Close"))
        
    def exec_(self, document, pos):
        self._doc = weakref.ref(document)
        super(TabContextMenu, self).exec_(pos)
    
    def docSave(self):
        doc = self._doc()
        if doc:
            self.parent().window().saveDocument(doc)
    
    def docSaveAs(self):
        doc = self._doc()
        if doc:
            self.parent().window().saveDocumentAs(doc)
    
    def docClose(self):
        doc = self._doc()
        if doc:
            self.parent().window().closeDocument(doc)


