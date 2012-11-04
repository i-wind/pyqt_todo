#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : dlg_newtask.py
@created : 2012-11-04 21:37:49.277
@changed : 2012-11-04 21:37:49.277
@creator : mkpy.py --version 0.0.26
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   :
"""
from __future__ import print_function

import os, sys
from argparse import ArgumentParser, Action, SUPPRESS
from PyQt4.QtCore import Qt, QSize, QDate, SIGNAL, SLOT, pyqtSlot
from PyQt4.QtGui import (QApplication, QDialog, QLabel, QLineEdit, QDateEdit, QSpinBox,
                         QComboBox, QPushButton, QGridLayout, QHBoxLayout)
from datetime import date


__revision__ = 1


def getRevision():
    """Callback method for -r/--revision option"""
    return str(__revision__)



class NewTaskDialog(QDialog):

    def __init__(self, parent=None):
        super(NewTaskDialog, self).__init__(parent)
        # task name
        nameLabel = QLabel(self.tr("Name:"))
        self.name = QLineEdit()
        nameLabel.setBuddy(self.name)
        # priority
        priorityLabel = QLabel(self.tr("Priority:"))
        self.priority = QComboBox()
        priorityLabel.setBuddy(self.priority)

        dateLabel = QLabel(self.tr("Deadline:"))
        self.deadline = QDateEdit()
        dateLabel.setBuddy(self.deadline)

        self.deadline.setCalendarPopup(True)
        self.deadline.calendarWidget().setFirstDayOfWeek(Qt.Monday)
        self.deadline.setDate(QDate(date.today()))

        createButton = QPushButton(self.tr("Save"))
        cancelButton = QPushButton(self.tr("Cancel"))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(createButton)
        buttonLayout.addWidget(cancelButton)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self.name, 0, 1)

        layout.addWidget(priorityLabel, 1, 0)
        layout.addWidget(self.priority, 1, 1)

        layout.addWidget(dateLabel, 2, 0)
        layout.addWidget(self.deadline, 2, 1)
        layout.addLayout(buttonLayout, 3, 0, 3, 2)
        self.setLayout(layout)

        self.connect(self.deadline, SIGNAL("dateChanged(const QDate&)"), self, SLOT("changed()"))
        self.connect(createButton, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.setWindowTitle(self.tr("Task"))
        self.resize(350, 120)
        self.setMinimumSize(QSize(250, 120))
        self.setMaximumSize(QSize(450, 120))


    @pyqtSlot()
    def changed(self):
        print(self.deadline.text())



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

    # program logic goes here...
    app = QApplication(sys.argv)
    dlg = NewTaskDialog()
    dlg.show()
    app.exec_()

# end of dlg_newtask.py
