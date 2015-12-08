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
import sqlite3 as sql
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

    def __init__(self, parent=None, workingDirectory=None, databasePath=None):

        super(RenameGUI, self).__init__(parent)
        self.parent = parent
        self.workingDirectory = workingDirectory
        self.databasePath = databasePath

        self.multiView = view.MultiView(self)
        self.paths = {}
        self.database = None
        self.databaseCursor = None

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidget(self.multiView)
        self.scrollArea.setWidgetResizable(True)

        self.layout = QtGui.QVBoxLayout(self)

        # persistent buttons
        buttonFrame = QtGui.QFrame(self)
        buttonLayout = QtGui.QHBoxLayout(buttonFrame)

        saveAllButton = QtGui.QPushButton(self)
        saveAllButton.setText("Save All")
        saveAllButton.clicked.connect(self.onSaveAllButtonClicked)
        buttonLayout.addWidget(saveAllButton)

        directoryButton = QtGui.QPushButton(self)
        directoryButton.setText("New Dataset")
        directoryButton.clicked.connect(self.onNewDatasetButtonClicked)
        buttonLayout.addWidget(directoryButton)

        databaseButton = QtGui.QPushButton(self)
        databaseButton.setText("Connect Database")
        databaseButton.clicked.connect(self.onDatabaseButtonClicked)
        buttonLayout.addWidget(databaseButton)

        self.layout.addWidget(buttonFrame)
        self.layout.addWidget(self.scrollArea)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if self.workingDirectory is not None:

            self.setWorkingDirectory(self.workingDirectory)

        if self.databasePath is not None:

            self.setDatabase(self.databasePath)

    def setDatabase(self, databasePath):

        self.database = sql.connect(databasePath)
        self.databaseCursor = self.database.cursor()

    def disconnectDatabase(self):

        if self.database is not None:
            self.database.close()
            self.database = None
            self.databaseCursor = None

    def onDatabaseButtonClicked(self):

        result = QtGui.QFileDialog.getOpenFileName(self)

        if result.endswith(".db"):
            self.disconnectDatabase()
            self.setDatabase(result)
        else:
            pass

    def setWorkingDirectory(self, workingDirectory):

        self.workingDirectory = os.path.abspath(workingDirectory)
        self.setWindowTitle(self.workingDirectory)
        self.multiView.removeAllViews()

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
            searches = ["Series Description", "Sequence Name", "Protocol Name"]
            leftLabel = dcm.valueFromSearch(searches, header, True)
            for search in searches:
                if search in leftLabel.keys():
                    if leftLabel[search] != '':
                        leftLabel = leftLabel[search]
                        break
            else:
                leftLabel = ''
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
            elif "other" in isDerived[1].keys():
                if len(isDerived[1]["other"]) == 1:
                    default = isDerived[1]["other"][0]
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

    def onDerivedCheckBoxChanged(self):

        buddy = self.sender().parent().parent().parent().interactors[-2]
        if self.sender().isChecked():
            buddy.show()
        else:
            buddy.hide()

    def onHeaderButtonClicked(self):

        interactor = self.sender().parent().parent().parent()
        path = self.paths[interactor.parent]
        currentSlice = interactor.parent.volumeView.currentSlice
        header = str(dicom.read_file(os.path.join(path, sorted(os.listdir(
            path))[currentSlice])))

        # display header in dialog
        modal = QtGui.QDialog(self)
        modalLayout = QtGui.QVBoxLayout(modal)
        modalText = QtGui.QTextEdit(modal)
        modalText.setReadOnly(True)
        modalText.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        modalText.textCursor().insertHtml(header.replace('\n', "<br>"))
        modalLayout.addWidget(modalText)
        modal.resize(QtCore.QSize(700, 500))
        modal.show()

    def save(self, viewInteractor):

        path = self.paths[viewInteractor]
        parentDirectory, name = os.path.split(path)
        interactors = viewInteractor.interactionWidget.interactors
        header = str(dicom.read_file(os.path.join(path, sorted(os.listdir(
                     path))[viewInteractor.volumeView.currentSlice])))

        # get data from inputs
        contrast = interactors[0].itemText(interactors[0].currentIndex())
        orientation = interactors[1].itemText(interactors[1].currentIndex())
        enhanced = interactors[2].isChecked()
        poorQuality = interactors[3].isChecked()
        review = interactors[4].isChecked()
        derived = interactors[5].isChecked()
        if derived:
            derivedType = interactors[6].itemText(
                interactors[6].currentIndex())
        else:
            derivedType = ""
        comment = interactors[7].text()

        # get data from header
        seriesNumber = dcm.findSeriesNumber(header)
        sequence = ' '.join(dcm.findSequence(header))
        vendor = dcm.findVendor(header)
        fieldStrength = dcm.findFieldStrength(header)
        echoTime, inversionTime, repetitionTime = dcm.findTimeParameters(
            header)

        # get data from folder structure
        directoryStem, date = os.path.split(self.workingDirectory)
        _, identifier = os.path.split(directoryStem)
        centerID, patientID = map(int, identifier.split('_'))

        # save and rename
        info = [str(seriesNumber), contrast, orientation]
        uniqueIdentifier = '_'.join(map(str, [centerID, patientID, date,
                                              seriesNumber]))

        if enhanced:
            info.insert(2, "CE")
        if derived:
            info.append(derivedType)
        newName = '_'.join(info)
        if newName == name:
            if self.database is not None:
                self.databaseCursor.execute(
                    'INSERT OR REPLACE INTO Series VALUES\
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (centerID, patientID, date, seriesNumber, contrast,
                     enhanced, orientation, sequence, derived, derivedType,
                     vendor, fieldStrength, echoTime, inversionTime,
                     repetitionTime, poorQuality, review, comment,
                     uniqueIdentifier))
                self.database.commit()
            return
        newPath = os.path.join(parentDirectory, newName)
        if os.path.exists(newPath):
            review = True
            if self.database is not None:
                self.databaseCursor.execute(
                    'INSERT OR REPLACE INTO Series VALUES\
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (centerID, patientID, date, seriesNumber, contrast,
                     enhanced, orientation, sequence, derived, derivedType,
                     vendor, fieldStrength, echoTime, inversionTime,
                     repetitionTime, poorQuality, review, comment,
                     uniqueIdentifier))
                self.database.commit()
            return
        else:
            os.rename(path, newPath)
            self.paths[viewInteractor] = newPath
            if self.database is not None:
                self.databaseCursor.execute(
                    'INSERT INTO Series VALUES\
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (centerID, patientID, date, seriesNumber, contrast,
                     enhanced, orientation, sequence, derived, derivedType,
                     vendor, fieldStrength, echoTime, inversionTime,
                     repetitionTime, poorQuality, review, comment,
                     uniqueIdentifier))
                self.database.commit()

    def onSaveButtonClicked(self):

        viewInteractor = self.sender().parent().parent().parent().parent
        self.save(viewInteractor)

    def onSaveAllButtonClicked(self):

        for viewInteractor in self.multiView.views:
            self.save(viewInteractor)

    def onNewDatasetButtonClicked(self):

        result = QtGui.QFileDialog.getExistingDirectory(self)
        tmp = self.workingDirectory

        if result:

            # check if lowest level folder
            try:
                self.setWorkingDirectory(result)
            except:
                self.setWorkingDirectory(tmp)

        else:
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
    inputFolder = "/home/jenspetersen/Desktop/BOVAREC/131_149/20130211/"
    database = "/home/jenspetersen/Desktop/BOVAREC.db"
#    inputFolder = "H:\\BOVAREC\\131_338\\20140401"
    multiView = RenameGUI()
#    multiView.setWorkingDirectory(inputFolder)
#    multiView.setDatabase(database)
    multiView.show()

    sys.exit(app.exec_())


# =============================================================================
# RUN
# =============================================================================


if __name__ == "__main__":

    main()
