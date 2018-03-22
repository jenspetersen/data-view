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

from E132Data.nrad import multi

import numpy as np
import sys

from matplotlib.figure import Figure
from matplotlib import cm

import qtpy
from qtpy.QtWidgets import (QWidget,
                            QVBoxLayout,
                            QHBoxLayout,
                            QGridLayout,
                            QApplication,
                            QFrame,
                            QLabel,
                            QLineEdit,
                            QComboBox,
                            QSpacerItem,
                            QSizePolicy)
from qtpy.QtCore import Signal, Slot, QSize, Qt

if qtpy.PYQT5:
    from matplotlib.backends.backend_qt5agg\
    import FigureCanvasQTAgg as FigureCanvas
elif qtpy.PYQT4:
    from matplotlib.backends.backend_qt4agg\
    import FigureCanvasQTAgg as FigureCanvas
else:
    raise ModuleNotFoundError("Could not import FigureCanvas. Please use PyQt4 or PyQt5.")

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

DEFAULT_FLOAT_CMAP = "gray"
DEFAULT_INT_CMAP = "magma"



class SliceView(QWidget):

    def __init__(self, data=None, imshow_args=None, parent=None, **kwargs):

        super(SliceView, self).__init__(parent, **kwargs)
        self.parent = parent
        self.data = data
        self.imshow_args = {} if imshow_args is None else imshow_args

        # make display available
        self.figure = Figure(facecolor="black")
        self.__canvas = FigureCanvas(self.figure)
        self.__imshowAccessor = None

        # layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.__canvas)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setDisabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        # prepare figure
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.axes.axis("Off")

        # plot if we can
        if self.data is not None:
            self.setData(self.data)

    def setData(self, data):

        assert data.ndim == 2, "data for VolumeView must be 2D"

        self.data = data

        if "cmap" not in self.imshow_args:
            if issubclass(data.dtype.type, np.integer):
                self.imshow_args["cmap"] = DEFAULT_INT_CMAP
            elif issubclass(data.dtype.type, np.floating):
                self.imshow_args["cmap"] = DEFAULT_FLOAT_CMAP
            else:
                pass

        if self.__imshowAccessor is None:
            self.__imshowAccessor = self.axes.imshow(data, **self.imshow_args)
        else:
            self.__imshowAccessor.set_data(data)
        self.__canvas.draw()

    def setParams(self, **kwargs):

        self.imshow_args.update(kwargs)
        self.__imshowAccessor = None
        if self.data is not None:
            self.setData(self.data)

    def sizeHint(self):
        return QSize(self.data.shape[1], self.data.shape[0])

    def aspectHint(self):
        return self.sizeHint().height / float(self.sizeHint().width)

    def heightForWidth(self, width):
        return width * self.aspectHint()



class VolumeView(QWidget):

    signalSliceChanged = Signal()

    def __init__(self, data=None, axis=0, parent=None, **kwargs):

        super(VolumeView, self).__init__(parent, **kwargs)
        self.parent = parent
        self.data = data

        if axis == -1:
            axis = 2
        if 0 <= axis <= 2:
            self.axis = axis
        else:
            raise IndexError("Index out of range.")

        # initialize variables
        self.numberOfSlices = 1
        self.currentSlice = 0

        # create single view
        self.sliceView = SliceView(parent=self)

        # layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.sliceView)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

        if self.data is not None:
            self.setData(self.data)

    def wheelEvent(self, event):

        try:
            delta = event.angleDelta().y()
        except AttributeError:
            delta = event.delta()

        slice_ = (self.currentSlice + int(delta / 120))\
            % self.numberOfSlices
        self.setSlice(slice_)

    def setData(self, data):

        assert data.ndim == 3, "data for VolumeView must be 3D"

        self.data = data
        self.setParams(vmin=np.min(data), vmax=np.max(data))
        self.data_min = np.min(data)
        self.data_max = np.max(data)
        self.numberOfSlices = self.data.shape[self.axis]
        self.setSlice(int(self.numberOfSlices / 2))

    def setSlice(self, sliceNumber):

        self.currentSlice = sliceNumber

        if self.axis == 0:
            self.sliceView.setData(self.data[sliceNumber])
        elif self.axis == 1:
            self.sliceView.setData(self.data[:, sliceNumber, :])
        elif self.axis == 2:
            self.sliceView.setData(self.data[:, :, sliceNumber])
        else:
            raise IndexError("Index out of range.")

        self.signalSliceChanged.emit()

    def setAxis(self, axis):

        if axis == -1: axis = 2
        if axis == self.axis: return

        if 0 <= axis <= 2:
            self.axis = axis
            self.numberOfSlices = self.data.shape[self.axis]
            self.setSlice(int(self.numberOfSlices / 2))
        else:
            raise IndexError("Index out of range.")

    def setParams(self, **kwargs):
        self.sliceView.setParams(**kwargs)

    def sizeHint(self):
        return self.sliceView.sizeHint()

    def aspectHint(self):
        return self.sliceView.aspectHint()

    def heightForWidth(self, width):
        return self.sliceView.heightForWidth(width)



class InteractionVolumeView(VolumeView):

    def __init__(self, label=None, **kwargs):

        super(InteractionVolumeView, self).__init__(**kwargs)

        self.interactionFrame = QFrame(self)
        self.interactionFrame.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.interactionFrame.setFixedHeight(30)
        self.interactionLayout = QHBoxLayout(self.interactionFrame)
        self.interactionLayout.setContentsMargins(5, 5, 5, 5)

        self.sliceLabel = QLabel(self.interactionFrame)
        self.sliceLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.updateSliceLabel()

        self.textLabel = QLineEdit(self.interactionFrame)
        self.textLabel.setReadOnly(True)
        self.textLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.textLabel.setAlignment(Qt.AlignCenter)
        stylesheet = \
            "QLineEdit {\n" \
            + "border: none;\n" \
            + "background-color: rgba(255, 255, 255, 0);\n" \
            + "}"
        self.textLabel.setStyleSheet(stylesheet)
        if label is not None:
            self.updateTextLabel(label)

        self.interactionLayout.addWidget(self.sliceLabel)
        self.interactionLayout.addWidget(self.textLabel)

        self.axisSelector = QComboBox(self.interactionFrame)
        self.axisSelector.setFixedWidth(40)
        self.axisSelector.insertItems(0, ["0", "1", "2"])
        self.interactionLayout.addWidget(self.axisSelector)

        self.layout.addWidget(self.interactionFrame)

        self.signalSliceChanged.connect(self.updateSliceLabel)
        self.axisSelector.currentIndexChanged.connect(self.setAxis)

    def updateSliceLabel(self):
        self.sliceLabel.setText("{}/{}".format(self.currentSlice, self.numberOfSlices))

    def updateTextLabel(self, text):
        self.textLabel.setText(text)
        self.textLabel.setCursorPosition(0)



class MultiView(QWidget):

    def __init__(self, views=None, data=None, labels=None, layout="horizontal", parent=None, **kwargs):

        super(MultiView, self).__init__(parent, **kwargs)

        self.parent = parent
        if layout == "horizontal":
            self.layout = QHBoxLayout(self)
        elif layout == "vertical":
            self.layout = QVBoxLayout(self)
        else:
            raise ValueError("layout must be 'horizontal' or 'vertical'.")
        self.views = []

        if views is not None:
            for view in views:
                self.addView(view)

        if data is not None:
            if data.ndim not in (3, 4):
                raise IndexError("Dimensionality of data must be 3 or 4.")
            if data.ndim == 3: data = data[np.newaxis, ...]
            for ax in range(data.shape[0]):
                current_label = labels[ax] if labels is not None else None
                self.addView(InteractionVolumeView(data=data[ax], label=current_label))

    def addView(self, view):

        self.views.append(view)
        self.layout.addWidget(view)

    def removeView(self, view):

        if isinstance(view, int):
            self.layout.itemAt(view).widget().setParent(None)
            self.views[view].deleteLater()
        else:
            for i, oldView in enumerate(self.views):
                if view == oldView:
                    self.removeView(i)
                    break



class RowMultiView(MultiView):
    def __init__(self, *args, **kwargs):
        kwargs["layout"] = "horizontal"
        super(RowMultiView, self).__init__(*args, **kwargs)



class ColumnMultiView(MultiView):
    def __init__(self, *args, **kwargs):
        kwargs["layout"] = "vertical"
        super(ColumnMultiView, self).__init__(*args, **kwargs)



def make_gridview(data, labels=None, identify_segmentations=True, column_kwargs=None, row_kwargs=None, volume_kwargs=None):

    if column_kwargs is None: column_kwargs = {}
    if row_kwargs is None: row_kwargs = {}
    if volume_kwargs is None: volume_kwargs = {}

    if data.ndim != 5:
        raise IndexError("Dimensionality of data must be 5.")

    colview = ColumnMultiView(**column_kwargs)
    seg_values = set()

    for i in range(data.shape[0]):
        volviews = []
        for j in range(data.shape[1]):
            current_data = data[i, j]
            if identify_segmentations:
                unique = np.unique(current_data)
                if len(unique) <= 64:
                    current_data = current_data.astpye(np.int16)
                    seg_values += set(unique)
            if labels is not None:
                volview = InteractionVolumeView(data=current_data, label=labels[i, j], **volume_kwargs)
            else:
                volview = InteractionVolumeView(data=current_data, **volume_kwargs)
            volviews.append(volview)
        rowview = RowMultiView(views=volviews, **row_kwargs)
        colview.addView(rowview)

    if len(seg_values) > 0:
        vmin = min(seg_values)
        vmax = max(seg_values)
        for rowview in colview.views:
            for view in rowview.views:
                if np.issubdtype(view.data.dtype, np.integer):
                    view.setParams(vmin=vmin, vmax=vmax)


    return colview


# =============================================================================
# MAIN METHOD
# =============================================================================


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    subject = multi.all_subjects()[0]
    data = multi.load(subjects=[subject])[subject]

    # labels = ["T1", "T1ce", "T2", "FLAIR", "T1ce - T1", "Segmentation", "Brain Mask"]

    # main = InteractionVolumeView(data=data[0, 5])
    main = make_gridview(data=data)
    main.show()

    sys.exit(app.exec_())
