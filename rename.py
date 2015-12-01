#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:AUTHOR: Jens Petersen
:ORGANIZATION: Heidelberg University Hospital; German Cancer Research Center
:CONTACT: jens.petersen@dkfz-heidelberg.de
:SINCE: Thu Nov 19 15:20:13 2015
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

import dicom
from misc import dcm
import os
import sys
import view

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
__date__ = 'Thu Nov 19 15:20:13 2015'
__version__ = '0.1'

# =============================================================================
# CLASSES
# =============================================================================


class RenameGUI(QtGui.QWidget):

    def __init__(self, parent=None, workingDirectory=None):

        super(RenameGUI, self).__init__(parent)
        self.parent = parent
        self.workingDirectory = workingDirectory

        self.multiView = view.MultiView(self)
        self.paths = {}
        self.headers = {}

#        self.scrollArea = QtGui.QScrollArea(self)
#        self.scrollArea.setWidget(self.multiView)
#        self.scrollArea.setWidgetResizable(True)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.multiView)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if self.workingDirectory is not None:

            self.setWorkingDirectory(self.workingDirectory)

    def setWorkingDirectory(self, workingDirectory):

        self.workingDirectory = os.path.abspath(workingDirectory)

        # working directory needs to contain DICOM folders
        for dataset in os.listdir(self.workingDirectory):

            datasetPath = os.path.join(self.workingDirectory, dataset)
            if len(os.listdir(datasetPath)) < 200:
                viewInteractor = view.VolumeViewInteraction(
                    data=dcm.volumeFromDCMDirectory(datasetPath),
                    interactionRows=2)
            else:
                viewInteractor = view.VolumeViewInteraction(
                    data=dcm.LazyDCMVolume(datasetPath),
                    interactionRows=2)

            # get header
            sliceNumber = viewInteractor.volumeView.currentSlice
            path = os.path.join(datasetPath,
                                sorted(os.listdir(datasetPath))[sliceNumber])
            header = str(dicom.read_file(path))

            # set label
            leftLabel = dcm.valueFromSearch("Series Description", header)
            if len(leftLabel["Series Description"]) == 0:
                leftLabel = ""
            else:
                leftLabel = leftLabel["Series Description"][0]
            viewInteractor.interactionWidget.setLeftLabel(leftLabel)

            # contrast combo box
            contrast = dcm.findContrast(header)
            sequence = dcm.findSequence(header)
            if contrast == "T2" and "FLAIR" in sequence:
                contrast = "FLAIR"
            viewInteractor.interactionWidget.addComboBox(
                sorted(dcm.allContrasts.keys() + ["UNKNOWN"]), contrast)

            # orientation combo box
            orientation = dcm.findOrientation(header)
            if orientation == "UNKNOWN":
                orientation = "ax"
            viewInteractor.interactionWidget.addComboBox(
                sorted(dcm.allOrientations))

            # contrast agent checkbox
            enhanced = dcm.isContrastEnhanced(header)
            viewInteractor.interactionWidget.addCheckBox("CE", "left",
                                                         enhanced, 1)

            # quality checkbox
            viewInteractor.interactionWidget.addCheckBox("LQ", "left")

            # review checkbox
            viewInteractor.interactionWidget.addCheckBox("RVW", "left")

            # derived checkbox
            isDerived = dcm.isDerived(header)
            viewInteractor.interactionWidget.addCheckBox("DRV", "left",
                                                         isDerived[0], 1)
            viewInteractor.interactionWidget.interactors[-1].stateChanged.\
                connect(self.onDerivedCheckBoxChanged)

            # view header button
            viewInteractor.interactionWidget.addButton("Header")
            viewInteractor.interactionWidget.buttons[-1].clicked.connect(
                self.onHeaderButtonClicked)

            # save button
            viewInteractor.interactionWidget.addButton("Save", 1)
            viewInteractor.interactionWidget.buttons[-1].clicked.connect(
                self.onSaveButtonClicked)

            # derivatives combobox
            derivativeOptions = []
            for key in dcm.allDerivatives.keys():
                derivativeOptions += dcm.allDerivatives[key]
            default = 0
            if contrast in isDerived[1].keys():
                if len(isDerived[1][contrast]) == 1:
                    default = isDerived[1][contrast][0]
            viewInteractor.interactionWidget.addComboBox(derivativeOptions,
                                                         default, 1)
            if isDerived[0]:
                viewInteractor.interactionWidget.interactors[-1].show()
            else:
                viewInteractor.interactionWidget.interactors[-1].hide()

            # comment line edit
            viewInteractor.interactionWidget.addLineEdit(row=1)

            # add view
            self.paths[viewInteractor] = datasetPath
            self.multiView.addView(viewInteractor)

            # connect
            viewInteractor.interactionWidget

    def onDerivedCheckBoxChanged(self):

        for i, interactor in enumerate(self.multiView.views):
            for j, box in enumerate(interactor.interactionWidget.interactors):
                if self.sender() == box:
                    if box.isChecked():
                        self.multiView.views[i].interactionWidget.\
                            interactors[-2].show()
                    else:
                        self.multiView.views[i].interactionWidget.\
                            interactors[-2].hide()

    def onHeaderButtonClicked(self):

        for i, interactor in enumerate(self.multiView.views):
            for j, button in enumerate(interactor.interactionWidget.buttons):
                if self.sender() == button:
                    print i, j

    def onSaveButtonClicked(self):

        for i, interactor in enumerate(self.multiView.views):
            for j, button in enumerate(interactor.interactionWidget.buttons):
                if self.sender() == button:

                    # get current info
                    path = self.paths[interactor]
                    contrast = interactor.interactionWidget.interactors[0].\
                        itemText(interactor.interactionWidget.interactors[0].
                                 currentIndex())
                    orientation = interactor.interactionWidget.interactors[1].\
                        itemText(interactor.interactionWidget.interactors[1].
                                 currentIndex())
                    enhanced = interactor.interactionWidget.interactors[2].\
                        isChecked()
                    poorQuality = interactor.interactionWidget.interactors[3].\
                        isChecked()
                    review = interactor.interactionWidget.interactors[4].\
                        isChecked()
                    derived = interactor.interactionWidget.interactors[5].\
                        isChecked()
                    derivedType = interactor.interactionWidget.interactors[6].\
                        itemText(interactor.interactionWidget.interactors[6].
                                 currentIndex())
                    comment = interactor.interactionWidget.interactors[7].\
                        text()

                    print path
                    print contrast, orientation, enhanced, poorQuality, review,
                    print derived, derivedType, comment

    def onSaveAllButtonClicked(self):

        pass


# =============================================================================
# METHODS
# =============================================================================


# =============================================================================
# MAIN METHOD
# =============================================================================


def main():

    app = QtGui.QApplication(sys.argv)

    # input path
    inputFolder = "/home/jenspetersen/Desktop/BOVAREC/131_149/20130111/"
#    inputFolder = "H:\\BOVAREC\\131_338\\20140401"
    multiView = RenameGUI()
    multiView.setWorkingDirectory(inputFolder)
    multiView.show()

    sys.exit(app.exec_())


# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
