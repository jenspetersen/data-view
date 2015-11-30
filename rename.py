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

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidget(self.multiView)
        self.scrollArea.setWidgetResizable(True)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.scrollArea)
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
                    data=dcm.volumeFromDCMDirectory(datasetPath))
            else:
                viewInteractor = view.VolumeViewInteraction(
                    data=dcm.LazyDCMVolume(datasetPath))

            # contrast combo box
            viewInteractor.interactionWidget.addComboBox(
                sorted(dcm.allContrasts))

            # orientation combo box
            viewInteractor.interactionWidget.addComboBox(
                sorted(dcm.allOrientations))

            # quality checkbox
            viewInteractor.interactionWidget.addCheckBox("LQ", "left")

            # review checkbox
            viewInteractor.interactionWidget.addCheckBox("RVW", "left")

            # derived checkbox
            checked = False
            viewInteractor.interactionWidget.addCheckBox("DRV", "left",
                                                         checked)

            # View header button
            viewInteractor.interactionWidget.addButton("Header")

            # Save button
            viewInteractor.interactionWidget.addButton("Save")

            # Derivatives combobox
            derivativeOptions = []
            for key in dcm.allDerivatives.keys():
                derivativeOptions += dcm.allDerivatives[key]
            viewInteractor.interactionWidget.addComboBox(derivativeOptions)
            if checked:
                viewInteractor.interactionWidget.interactors[-1].show()
            else:
                viewInteractor.interactionWidget.interactors[-1].hide()

            self.paths[viewInteractor] = datasetPath
            self.multiView.addView(viewInteractor)

    def onDerivedCheckBoxChanged():

        pass

    def onHeaderButtonClicked():

        pass

    def onSaveButtonClicked():

        pass

    def onSaveAllButtonClicked():

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
#    inputFolder = "/home/jenspetersen/Desktop/BOVAREC/131_149/20130111/"
    inputFolder = "H:\\BOVAREC\\131_338\\20140401"
    multiView = RenameGUI()
    multiView.setWorkingDirectory(inputFolder)
    multiView.show()

    sys.exit(app.exec_())


# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
