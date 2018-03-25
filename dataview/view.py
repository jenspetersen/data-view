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

import argparse
import json
import numpy as np
import os
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

    signalSliceChanged = Signal(int)
    signalSyncSlices = Signal(int)

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

        self.signalSliceChanged.emit(slice_)

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.signalSyncSlices.emit(slice_)

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

    signalAxisChanged = Signal(int)

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
        self.axisSelector.currentIndexChanged.connect(self.setAxisAndEmit)

    def setAxisAndEmit(self, axis):
        self.setAxis(axis)
        self.signalAxisChanged.emit(axis)

    def setAxis(self, axis):
        super(InteractionVolumeView, self).setAxis(axis)
        self.axisSelector.setCurrentIndex(axis)
        self.updateSliceLabel()

    def setSlice(self, slice_):
        super(InteractionVolumeView, self).setSlice(slice_)
        self.updateSliceLabel()

    def updateSliceLabel(self):
        try:
            length = str(len(str(self.numberOfSlices)))
            self.sliceLabel.setText(("{:0" + length + "d}/{:0" + length + "}").format(self.currentSlice, self.numberOfSlices))
        except AttributeError:
            pass

    def updateTextLabel(self, text):
        try:
            self.textLabel.setText(text)
            self.textLabel.setCursorPosition(0)
        except AttributeError:
            pass



class MultiView(QWidget):

    signalSyncSlices = Signal(int)
    signalAxisChanged = Signal(int)

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
        if hasattr(view, "signalAxisChanged"):
            view.signalAxisChanged.connect(self.on_signalAxisChanged)
        if hasattr(view, "signalSyncSlices"):
            view.signalSyncSlices.connect(self.on_signalSyncSlices)

    def removeView(self, view):

        if isinstance(view, int):
            self.layout.itemAt(view).widget().setParent(None)
            self.views[view].deleteLater()
        else:
            for i, oldView in enumerate(self.views):
                if view == oldView:
                    self.removeView(i)
                    break

    def setAxis(self, axis):
        for view in self.views:
            view.setAxis(axis)

    def setSlice(self, slice_):
        for view in self.views:
            view.setSlice(slice_)

    def __getitem__(self, idx):
        return self.views[idx]

    def on_signalAxisChanged(self, axis):
        self.setAxis(axis)
        self.signalAxisChanged.emit(axis)

    def on_signalSyncSlices(self, slice_):
        self.setSlice(slice_)
        self.signalSyncSlices.emit(slice_)



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
    seg_ids = []

    for i in range(data.shape[0]):
        volviews = []
        for j in range(data.shape[1]):
            current_data = data[i, j, ...]
            if identify_segmentations:
                unique = np.unique(current_data)
                if len(unique) <= 64:
                    seg_values.update(unique)
                    seg_ids.append((i, j))
            if labels is not None:
                volview = InteractionVolumeView(data=current_data, label=labels[i][j], **volume_kwargs)
            else:
                volview = InteractionVolumeView(data=current_data, **volume_kwargs)
            volviews.append(volview)
        rowview = RowMultiView(views=volviews, **row_kwargs)
        colview.addView(rowview)

    if len(seg_ids) > 0:
        vmin = min(seg_values)
        vmax = max(seg_values)
        for id_ in seg_ids:
            colview[id_[0]][id_[1]].setParams(vmin=vmin, vmax=vmax, cmap=DEFAULT_INT_CMAP)

    return colview

# =============================================================================
# MAIN METHOD
# =============================================================================

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("objects", type=str, nargs="+",
                        help="Files or directories to load.")
    parser.add_argument("-ns", "--no-segmentations", action="store_true")
    parser.add_argument("-nm", "--no-memmap", action="store_true")
    parser.add_argument("--column-kwargs", default="{}")
    parser.add_argument("--row-kwargs", default="{}")
    parser.add_argument("--volume-kwargs", default="{}")
    args = parser.parse_args()

    column_kwargs = json.loads(args.column_kwargs)
    row_kwargs = json.loads(args.row_kwargs)
    volume_kwargs = json.loads(args.volume_kwargs)
    mmap = None if args.no_memmap else "r"

    app = QApplication(sys.argv)

    data = []
    labels = []

    for o, obj in enumerate(args.objects):

        current_data = np.load(obj, mmap)
        current_label = os.path.basename(obj).split(".")[0]

        if o >= 1 and current_data.ndim != data[-1].ndim:
            raise IndexError("All loaded datasets must have the same dimensionality.")

        if current_data.ndim not in (3, 4, 5):
            raise IndexError("Can only load datasets with dimension 3, 4 or 5.")

        if o >= 1 and current_data.ndim >=5:
            raise IndexError("When loading multiple datasets, the dimensionality of each can't be greater than 4.")

        if current_data.ndim == 4:
            current_label = [current_label + "-" + str(i) for i in range(current_data.shape[0])]

        if current_data.ndim == 5:
            col_label = []
            for i in range(current_data.shape[0]):
                row_label = []
                for j in range(current_data.shape[1]):
                    row_label.append(current_label + "-" + "{},{}".format(i, j))
                col_label.append(row_label)
            current_label = col_label

        data.append(current_data)
        labels.append(current_label)

    data = np.array(data)

    if data.ndim == 4:
        data = data[np.newaxis, ...]
        labels = [labels]

    if data.ndim == 6:
        data = data[0]
        labels = labels[0]

    main = make_gridview(data, labels=labels, identify_segmentations=not args.no_segmentations,
                         column_kwargs=column_kwargs, row_kwargs=row_kwargs, volume_kwargs=volume_kwargs)

    main.show()

    sys.exit(app.exec_())

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    main()
