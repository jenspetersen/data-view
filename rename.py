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
import numpy as np
import os
import re
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


def findSliceNumber(DCMString):

    pattern = re.compile(
        "\n\(\w{4}\,\s\w{4}\)\s.*Slice Number.*[A-Z]{2}\:\s\'\s*\d+\s*\'\n")
    result = re.findall(pattern, DCMString)
    return int(re.search("\'\s*\d+\s*\'", result[0]).group(0)[1:-1])


def dataFromDICOMDir(directory):

    directory = os.path.abspath(directory)
    slices = {}

    for DCMFile in os.listdir(directory):
        DCMData = dicom.read_file(os.path.join(directory, DCMFile))
        sliceNumber = findSliceNumber(str(DCMData))
        slices[sliceNumber] = DCMData.pixel_array

    dataShape = [len(slices)] + list(slices[1].shape)
    dataVolume = np.zeros(dataShape)

    for sl in slices:
        dataVolume[sl - 1, :] = slices[sl]

    return dataVolume


class RenameGUI(QtGui.QWidget):

    def __init__(self, workingDirectory=None, parent=None):

        super(RenameGUI, self).__init__(parent)
        self.workingDirectory = os.path.abspath(workingDirectory)
        self.parent = parent

        self.multiView = view.MultiView(self)
        self.paths = {}

        if self.workingDirectory is not None:

            # working directory needs to contain DICOM folders
            for dataset in os.listdir(self.workingDirectory):

                datasetPath = os.path.join(self.workingDirectory, dataset)
                viewInteractor = view.VolumeViewInteraction()
                self.paths[viewInteractor] = datasetPath
                self.multiView.addView(viewInteractor)

                # create the dataset


    def setWorkingDirectory(self, workingDirectory):

        self.__init__(workingDirectory, self.parent)


# =============================================================================
# METHODS
# =============================================================================


# =============================================================================
# MAIN METHOD
# =============================================================================


def main():

    app = QtGui.QApplication(sys.argv)

    # input path
    inputFolder = "/home/jenspetersen/Desktop/BOVAREC/131_149/20130111/0301_NOCONTRAST_FFE"
    interactor = view.VolumeViewInteraction(data=dataFromDICOMDir(inputFolder))
    interactor.show()

    sys.exit(app.exec_())

#    mainview = MultiView()

# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
