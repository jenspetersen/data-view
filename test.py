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
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.__canvas)
        self.layout.setContentsMargins(0, 0, 0, 0)
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
        self.setMinimumSize(max(data.shape[0], 10),
                            max(data.shape[1], 10))


class VolumeView(QtGui.QWidget):

    def __init__(self, parent=None, data=None, axis=0):

        super(VolumeView, self).__init__(parent)
        self.parent = parent
        self.data = data
        self.axis = axis

        # create single view
        self.sliceView = SliceView(self)

        # layout
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.sliceView)
        self.layout.setContentsMargins(0, 0, 0, 0)

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


class InteractionWidget(QtGui.QWidget):

    def __init__(self, parent=None):

        super(InteractionWidget, self).__init__(parent)

        self.buttons = []
        self.interactors = []

        # outer layout
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Fixed)

        # label container
        self.labelFrame = QtGui.QFrame(self)
        self.labelFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.labelLayout = QtGui.QHBoxLayout(self.labelFrame)
        self.labelLayout.setContentsMargins(5, 5, 5, 0)

        # labels
        self.leftLabel = QtGui.QLabel(self.labelFrame)
        self.rightLabel = QtGui.QLabel(self.labelFrame)
        self.rightLabel.setAlignment(QtCore.Qt.AlignRight |
                                     QtCore.Qt.AlignTrailing)

        self.labelLayout.addWidget(self.leftLabel)
        labelSpacer = QtGui.QSpacerItem(10, 20,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Minimum)
        self.labelLayout.addItem(labelSpacer)
        self.labelLayout.addWidget(self.rightLabel)

        # interaction outer container
        self.interactionFrame = QtGui.QFrame(self)
        self.interactionFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.interactionLayout = QtGui.QHBoxLayout(self.interactionFrame)
        self.interactionLayout.setContentsMargins(0, 0, 0, 0)

        # interaction button container
        self.buttonFrame = QtGui.QFrame(self.interactionFrame)
        self.buttonFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.buttonLayout = QtGui.QHBoxLayout(self.buttonFrame)
        self.buttonLayout.setContentsMargins(5, 5, 5, 5)

        # interaction inner container
        self.interactionInnerFrame = QtGui.QFrame(self.interactionFrame)
        self.interactionInnerFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.interactionInnerLayout = QtGui.QHBoxLayout(
            self.interactionInnerFrame)
        self.interactionInnerLayout.setContentsMargins(5, 5, 5, 0)

        self.interactionLayout.addWidget(self.interactionInnerFrame)
        interactionSpacer = QtGui.QSpacerItem(10, 20,
                                              QtGui.QSizePolicy.Expanding,
                                              QtGui.QSizePolicy.Minimum)
        self.interactionLayout.addItem(interactionSpacer)
        self.interactionLayout.addWidget(self.buttonFrame)

        # outer layout
        self.layout.addWidget(self.labelFrame)
        self.layout.addWidget(self.interactionFrame)

    def setLeftLabel(self, labelText):

        self.leftLabel.setText(labelText)

    def setRightLabel(self, labelText):

        self.rightLabel.setText(labelText)

    def addButton(self, buttonText):

        self.buttons.append(QtGui.QPushButton(self.buttonFrame))
        self.buttons[-1].setText(buttonText)
        self.buttonLayout.addWidget(self.buttons[-1])

    def removeButton(self, buttonID):

        self.buttonLayout.removeWidget(self.buttons[buttonID])
        del self.buttons[buttonID]

    def addLineEdit(self, lineEditText=''):

        self.interactors.append(QtGui.QLineEdit(self.interactionInnerFrame))
        self.interactors[-1].setText(lineEditText)
        self.interactionInnerLayout.addWidget(self.interactors[-1])

    def addCheckBox(self, checkBoxText):

        self.interactors.append(QtGui.QCheckBox(self.interactionInnerFrame))
        self.interactors[-1].setText(checkBoxText)
        self.interactionInnerLayout.addWidget(self.interactors[-1])

    def addComboBox(self, options):

        self.interactors.append(QtGui.QComboBox(self.interactionInnerFrame))
        for option in options:
            self.interactors[-1].addItem(option)
        self.interactors[-1].setCurrentIndex(0)
        self.interactionInnerLayout.addWidget(self.interactors[-1])

    def removeInteractor(self, interactorID):

        self.interactionInnerLayout.removeWidget(
            self.interactors[interactorID])
        del self.interactors[interactorID]


class VolumeViewInteraction(QtGui.QWidget):

    def __init__(self, parent=None, data=None, axis=0, position="bottom"):

        # check inputs
        if position not in ["top", "bottom"]:
            raise ValueError("Position must be either 'top' or 'bottom'")

        super(VolumeViewInteraction, self).__init__(parent)

        # initialize children
        self.volumeView = VolumeView(self, data, axis)
        self.interactionWidget = InteractionWidget(self)

        # layout
        self.layout = QtGui.QVBoxLayout(self)
        if position == "top":
            self.layout.addWidget(self.interactionWidget)
            self.layout.addWidget(self.volumeView)
        elif position == "bottom":
            self.layout.addWidget(self.volumeView)
            self.layout.addWidget(self.interactionWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.interactionWidget.setRightLabel("0/0")

    def setData(self, data):

        self.volumeView.setData(data)


# =============================================================================
# MAIN METHOD
# =============================================================================


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    main = VolumeViewInteraction(data=np.random.rand(100, 100, 100))
    main.show()

    sys.exit(app.exec_())
