#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

:AUTHOR: Jens Petersen
:ORGANIZATION: Heidelberg University Hospital; German Cancer Research Center
:CONTACT: jens.petersen@dkfz.de
:SINCE: Fri Nov 13 11:09:17 2015
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

import nibabel as nib
import numpy as np
import sys

# matplotlib
from matplotlib.backends import qt_compat
from matplotlib.backends.backend_qt4agg\
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm

# Qt
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

# =============================================================================
# PROGRAM METADATA
# =============================================================================

__author__ = "Jens Petersen"
__email__ = "jens.petersen@dkfz.de"
__copyright__ = ""
__license__ = ""
__date__ = "Fri Nov 13 11:09:17 2015"
__version__ = "0.1"

# =============================================================================
# METHODS & CLASSES
# =============================================================================


class SliceView(QtGui.QWidget):

    def __init__(self, parent=None, data=None):

        super(SliceView, self).__init__(parent)

        # make display available
        self.data = data
        self.figure = Figure(facecolor="black")
        self.__canvas = FigureCanvas(self.figure)
        self.__imshowAccessor = None

        # layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.__canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setDisabled(True)

        # prepare figure
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.axes.axis("Off")

        # plot if we can
        if data is not None:
            self.setData(data)

    def setData(self, data):

        if not self.__imshowAccessor:
            self.__imshowAccessor = self.axes.imshow(data, cmap=cm.gray)
            self.__canvas.draw()
        else:
            self.__imshowAccessor.set_data(data)
            self.__canvas.draw()


class VolumeView(QtGui.QWidget):

    def __init__(self, parent=None, data=None, axis=0):

        super(VolumeView, self).__init__(parent)
        self.data = data
        self.axis = axis

        # create single view
        self.sliceView = SliceView(self)

        # layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.sliceView)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        if self.data is not None:

            self.numberOfSlices = self.data.shape[self.axis]
            self.currentSlice = int(self.numberOfSlices / 2)
            self.setSlice(self.currentSlice)

    def wheelEvent(self, event):
        self.currentSlice = (self.currentSlice + int(event.delta() / 120))\
            % self.numberOfSlices
        print self.currentSlice
        self.setSlice(self.currentSlice)

    def setData(self, data):
        self.__init__(self.parent, data, self.axis)

    def setSlice(self, sliceNumber):
        if self.axis == 0:
            self.sliceView.setData(self.data[sliceNumber, :, :])
        elif self.axis == 1:
            self.sliceView.setData(self.data[:, sliceNumber, :])
        elif self.axis == 2:
            self.sliceView.setData(self.data[:, :, sliceNumber])
        else:
            raise IndexError("Index out of range.")

    def setAxis(self, axis):
        if not isinstance(axis, int):
            raise ValueError("Index must be integer.")
        if 0 <= axis <= 2:
            self.axis = axis
            self.numberOfSlices = self.data.shape[self.axis]
            self.currentSlice = int(self.numberOfSlices / 2)
            self.setSlice(self.currentSlice)
        else:
            raise IndexError("Index out of range.")


# =============================================================================
# MAIN METHOD
# =============================================================================


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    main = VolumeView(data=np.random.rand(100, 100, 100))
    main.show()

    sys.exit(app.exec_())
