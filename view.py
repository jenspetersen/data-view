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
        self.parent = parent
        self.data = data

        # make display available
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
        if self.data is not None:
            self.setData(self.data)

    def setData(self, data):

        self.data = data
        if self.__imshowAccessor is None:
            self.__imshowAccessor = self.axes.imshow(data, cmap=cm.gray)
            self.__canvas.draw()
        else:
            self.__imshowAccessor.set_data(data)
            self.__canvas.draw()
        aspectRatio = data.shape[1] / float(data.shape[0])
        if aspectRatio < 1:
            self.setMinimumSize(50 * aspectRatio, 50)
        else:
            self.setMinimumSize(50, 50 / aspectRatio)


class VolumeView(QtGui.QWidget):

    def __init__(self, parent=None, data=None, axis=0):

        super(VolumeView, self).__init__(parent)
        self.parent = parent
        self.data = data
        self.axis = axis

        # initialze variables
        self.numberOfSlices = 1
        self.currentSlice = 0

        # create single view
        self.sliceView = SliceView(self)

        # layout
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.sliceView)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if self.data is not None:

            self.setData(self.data)

    def wheelEvent(self, event):

        self.currentSlice = (self.currentSlice + int(event.delta() / 120))\
            % self.numberOfSlices
        self.setSlice(self.currentSlice)

    def setData(self, data):

        self.data = data
        self.numberOfSlices = self.data.shape[self.axis]
        self.currentSlice = int(self.numberOfSlices / 2)
        self.setSlice(self.currentSlice)
        self.setMinimumSize(self.sliceView.minimumSize())

    def setSlice(self, sliceNumber):

        if self.axis == 0:
            self.sliceView.setData(self.data[sliceNumber])
        elif self.axis == 1:
            self.sliceView.setData(self.data[:, sliceNumber, :])
        elif self.axis == 2:
            self.sliceView.setData(self.data[:, :, sliceNumber])
        else:
            raise IndexError("Index out of range.")
        self.emit(QtCore.SIGNAL("sliceChanged"))

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

    def __init__(self, parent=None, rows=1):

        super(InteractionWidget, self).__init__(parent)
        self.parent = parent

        # initialize variables
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

        self.layout.addWidget(self.labelFrame)

        self.interactionFrames = []
        self.interactionLayouts = []
        self.buttonFrames = []
        self.buttonLayouts = []
        self.interactionInnerFrames = []
        self.interactionInnerLayouts = []

        for i in range(rows):

            # interaction outer container
            self.interactionFrames.append(QtGui.QFrame(self))
            self.interactionFrames[-1].setFrameShape(QtGui.QFrame.NoFrame)
            self.interactionLayouts.append(
                QtGui.QHBoxLayout(self.interactionFrames[-1]))
            self.interactionLayouts[-1].setContentsMargins(0, 0, 0, 0)

            # interaction button container
            self.buttonFrames.append(QtGui.QFrame(self.interactionFrames[-1]))
            self.buttonFrames[-1].setFrameShape(QtGui.QFrame.NoFrame)
            self.buttonLayouts.append(QtGui.QHBoxLayout(self.buttonFrames[-1]))
            self.buttonLayouts[-1].setContentsMargins(5, 5, 5, 5)

            # interaction inner container
            self.interactionInnerFrames.append(
                QtGui.QFrame(self.interactionFrames[-1]))
            self.interactionInnerFrames[-1].setFrameShape(QtGui.QFrame.NoFrame)
            self.interactionInnerLayouts.append(
                QtGui.QHBoxLayout(self.interactionInnerFrames[-1]))
            self.interactionInnerLayouts[-1].setContentsMargins(5, 5, 5, 0)

            self.interactionLayouts[-1].addWidget(
                self.interactionInnerFrames[-1])
            interactionSpacer = QtGui.QSpacerItem(10, 20,
                                                  QtGui.QSizePolicy.Expanding,
                                                  QtGui.QSizePolicy.Minimum)
            self.interactionLayouts[-1].addItem(interactionSpacer)
            self.interactionLayouts[-1].addWidget(self.buttonFrames[-1])

            self.layout.addWidget(self.interactionFrames[-1])

    def setLeftLabel(self, labelText):

        self.leftLabel.setText(labelText)

    def setRightLabel(self, labelText):

        self.rightLabel.setText(labelText)

    def addButton(self, buttonText, row=0):

        self.buttons.append(QtGui.QPushButton(self.buttonFrames[row]))
        self.buttons[-1].setText(buttonText)
        self.buttonLayouts[row].addWidget(self.buttons[-1])

        # want to adjust button to text width
#        label = QtGui.QLabel()
#        label.setText(buttonText)
#        width = label.fontMetrics().boundingRect(label.text()).width()
#        self.buttons[-1].setFixedWidth(width)
#        self.buttons[-1].setContentsMargins(5, 5, 5, 5)

    def removeButton(self, buttonID):

        for layout in self.buttonLayouts:
            try:
                layout.removeWidget(self.buttons[buttonID])
            except:
                pass
        del self.buttons[buttonID]

    def addLineEdit(self, lineEditText='', row=0):

        self.interactors.append(QtGui.QLineEdit(
            self.interactionInnerFrames[-1]))
        self.interactors[-1].setText(lineEditText)
        self.interactionInnerLayouts[row].addWidget(self.interactors[-1])

    def addCheckBox(self, checkBoxText, textPosition="right", default=False,
                    row=0):

        self.interactors.append(QtGui.QCheckBox(
            self.interactionInnerFrames[-1]))
        self.interactors[-1].setText(checkBoxText)
        if textPosition == "right":
            self.interactors[-1].setLayoutDirection(QtCore.Qt.LeftToRight)
        elif textPosition == "left":
            self.interactors[-1].setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            raise ValueError("textPosition must be left or right")
        self.interactors[-1].setChecked(default)
        self.interactionInnerLayouts[row].addWidget(self.interactors[-1])

    def addComboBox(self, options, default=0, row=0):

        self.interactors.append(QtGui.QComboBox(
            self.interactionInnerFrames[-1]))
        for option in options:
            self.interactors[-1].addItem(option)
        if isinstance(default, str):
            default = options.index(default)
        self.interactors[-1].setCurrentIndex(default)
        self.interactionInnerLayouts[row].addWidget(self.interactors[-1])

    def removeInteractor(self, interactorID):

        for layout in self.interactionInnerLayouts:
            try:
                layout.removeWidget(self.interactors[interactorID])
            except:
                pass
        del self.interactors[interactorID]


class VolumeViewInteraction(QtGui.QWidget):

    def __init__(self, parent=None, data=None, axis=0, position="bottom",
                 interactionRows=1):

        super(VolumeViewInteraction, self).__init__(parent)
        self.parent = parent
        self.data = data
        self.axis = axis
        self.position = position

        # initialize children
        self.volumeView = VolumeView(self, None, axis)
        self.interactionWidget = InteractionWidget(self, interactionRows)

        # layout
        self.layout = QtGui.QVBoxLayout(self)
        if self.position == "top":
            self.layout.addWidget(self.interactionWidget)
            self.layout.addWidget(self.volumeView)
        elif self.position == "bottom":
            self.layout.addWidget(self.volumeView)
            self.layout.addWidget(self.interactionWidget)
        else:
            raise ValueError("Position must be 'top' or 'bottom'.")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # connect signals
        self.connect(self.volumeView, QtCore.SIGNAL("sliceChanged"),
                     self.updateSliceLabel)

        # set data
        if data is not None:
            self.setData(data)

    def setData(self, data):

        self.data = data
        self.volumeView.setData(data)
#        self.setMinimumWidth(self.volumeView.minimumWidth())

    def setAxis(self, axis):

        self.axis = axis
        self.volumeView.setAxis(axis)

    def updateSliceLabel(self):

        # note that we print the slice number starting at 1 rather than 0
        self.interactionWidget.setRightLabel(
            "{}/{}".format(self.volumeView.currentSlice + 1,
                           self.volumeView.numberOfSlices))


class MultiView(QtGui.QWidget):

    def __init__(self, parent=None):

        super(MultiView, self).__init__(parent)
        self.parent = parent

        self.views = []
        self.layout = QtGui.QGridLayout(self)

    def addView(self, view):

        self.views.append(view)
        self.updateLayout()

    def removeView(self, view):

        if isinstance(view, int):
            del self.views[view]
        else:
            for i, oldView in enumerate(self.views):
                if view == oldView:
                    del self.views[i]
                    break
        self.updateLayout()

    def updateLayout(self):

        # find maximum height and width of single views
        itemHeight = 1
        itemWidth = 1
        for view in self.views:
            dimensions = list(view.data.shape)
            del dimensions[view.axis]
            itemHeight = max(itemHeight, dimensions[1])
            itemWidth = max(itemWidth, dimensions[0])

        itemWidth /= itemHeight
        itemHeight = 1

        # find best layout
        targetAspect = self.width() / float(self.height())
        lowerAspect = targetAspect
        numberOfColumns = len(self.views)
        numberOfRows = 1
        upperAspect = numberOfColumns * itemWidth / float(itemHeight)

        while upperAspect > targetAspect:
            if numberOfColumns == 1:
                break
            numberOfColumns -= 1
            numberOfRows = int(np.ceil(len(self.views) / numberOfColumns))
            currentAspect = (numberOfColumns * itemWidth /
                             float(numberOfRows * itemHeight))
            if currentAspect > targetAspect:
                upperAspect = currentAspect
            else:
                lowerAspect = currentAspect
                break

        if (targetAspect / lowerAspect) > (upperAspect / targetAspect):
            numberOfColumns += 1

        # now have ideal number of rows and columns
        # clear layout and insert widgets again (could be optimized)
        for view in enumerate(self.views):
            try:
                self.layout.removeWidget(view)
            except:
                pass
        for i, view in enumerate(self.views):
            self.layout.addWidget(view, i / numberOfColumns,
                                  i % numberOfColumns)

    def resizeEvent(self, evt=None):

        self.updateLayout()


# =============================================================================
# MAIN METHOD
# =============================================================================


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    main = MultiView()
    for i in range(10):
        dims = np.random.randint(50, 100, 3)
        currentView = VolumeViewInteraction(main,   np.random.rand(*dims),
                                            interactionRows=2)
        currentView.interactionWidget.addButton("OK")
        currentView.interactionWidget.addButton("Test", 1)
        main.addView(currentView)
    main.show()

    sys.exit(app.exec_())
