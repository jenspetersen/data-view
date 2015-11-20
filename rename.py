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
from misc.lazy import LazyProperty
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


class LazyDCMVolume(object):

    def __init__(self, dataDirectory=None):

        if dataDirectory is not None:
            self.setDataDirectory(dataDirectory)

    def setDataDirectory(self, dataDirectory):

        self.dataDirectory = os.path.abspath(dataDirectory)
        self.fileList = map(lambda x: os.path.join(dataDirectory, x),
                            os.listdir(dataDirectory))
        self.__data = {}
#        self.__data = np.zeros(self.shape)
#        self.__track = []

    @LazyProperty
    def shape(self):

        centerSlice = int(len(self.fileList) / 2)
#        self.__data[centerSlice, :, :] = dicom.read_file(
#            self.fileList[centerSlice]).pixel_array
        self.__data[centerSlice] = dicom.read_file(
            self.fileList[centerSlice]).pixel_array
#        self.__track.append(centerSlice)
        sliceDimensions = self.__data[centerSlice].shape
        return tuple([len(self.fileList)] + list(sliceDimensions))

    def __len__(self):

        return self.shape[0]

    def __getitem__(self, key):

        if key not in self.__data:
            self.__data[key] = dicom.read_file(self.fileList[key]).pixel_array
        return self.__data[key]

#        if isinstance(key, int):
#
#            if key not in self.__track:
#                self.__data[key, :, :] = dicom.read_file(
#                    self.fileList[key]).pixel_array
#                self.__track.append(key)
#            return self.__data[key, :, :]
#
#        elif isinstance(key, slice):
#
#            for index in range(key.indices(len(self))):
#
#                if index not in self.__track:
#                    self.__data[index, :, :] = dicom.read_file(
#                        self.fileList[index]).pixel_array
#                    self.__track.append(index)
#
#            return self.__data[slice]
#
#        elif isinstance(key, tuple):
#
#            pass





class RenameGUI(QtGui.QWidget):

    def __init__(self, parent=None, workingDirectory=None):

        super(RenameGUI, self).__init__(parent)
        self.parent = parent
        self.workingDirectory = workingDirectory

        self.multiView = view.MultiView(self)
        self.paths = {}

        if self.workingDirectory is not None:

            self.workingDirectory = os.path.abspath(self.workingDirectory)

            # working directory needs to contain DICOM folders
            for dataset in os.listdir(self.workingDirectory):

                datasetPath = os.path.join(self.workingDirectory, dataset)
                viewInteractor = view.VolumeViewInteraction(
                    data=dataFromDICOMDir(datasetPath))
                self.paths[viewInteractor] = datasetPath
                self.multiView.addView(viewInteractor)

    def setWorkingDirectory(self, workingDirectory):

        self.__init__(self.parent, workingDirectory)


# =============================================================================
# METHODS
# =============================================================================


# =============================================================================
# MAIN METHOD
# =============================================================================


def main():

    app = QtGui.QApplication(sys.argv)

    # input path
    inputFolder = "/home/jenspetersen/Desktop/BOVAREC/131_149/20130111/0301_NOCONTRAST_FFE/"
    data = LazyDCMVolume(inputFolder)
    multiView = view.VolumeView(data=data)
    multiView.show()
#    multiView = RenameGUI()
#    multiView.setWorkingDirectory(inputFolder)

    sys.exit(app.exec_())


# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
