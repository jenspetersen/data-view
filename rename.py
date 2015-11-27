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

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.multiView)

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
            self.paths[viewInteractor] = datasetPath
            self.multiView.addView(viewInteractor)


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
