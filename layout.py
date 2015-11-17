#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:AUTHOR: Jens Petersen
:ORGANIZATION: Heidelberg University Hospital; German Cancer Research Center
:CONTACT: jens.petersen@dkfz-heidelberg.de
:SINCE: Tue Nov 17 16:10:06 2015
:VERSION: 0.1

DESCRIPTION
-----------



REQUIRES
--------



TODO
----



"""

# =============================================================================
# IMPORT STATEMENTS
# =============================================================================

# Qt
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

# =============================================================================
# PROGRAM METADATA
# =============================================================================

__author__ = 'Jens Petersen'
__email__ = 'jens.petersen@dkfz-heidelberg.de'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Nov 17 16:10:06 2015'
__version__ = '0.1'

# =============================================================================
# CLASSES
# =============================================================================


class FlowLayout(QtGui.QLayout):

    def __init__(self, parent=None, margin=0, spacing=-1):

        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setMargin(margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):

        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):

        self.itemList.append(item)

    def count(self):

        return len(self.itemList)

    def itemAt(self, index):

        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):

        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):

        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):

        return True

    def heightForWidth(self, width):

        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):

        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):

        return self.minimumSize()

    def minimumSize(self):

        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):

        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y),
                                              item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


# =============================================================================
# METHODS
# =============================================================================


# =============================================================================
# MAIN METHOD
# =============================================================================


def main():

    pass

# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
