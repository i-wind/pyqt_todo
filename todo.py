#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : todo.py
@created : 2012-11-04 00:14:14.281
@changed : 2012-11-04 01:23:03.937
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
"""
from __future__ import print_function

import os, sys
from PyQt4 import QtGui, QtCore
from db.sqlite import SQLite


APP_DIR = os.path.dirname( __file__ )


__version__  = (0, 0, 2)


def getVersion():
    """Version number in string format"""
    return '.'.join(map(str, __version__))



class QCCLog(object):
    """ Used for logging for background process """
    def __init__(self, obj):
        self._obj = obj

    def write(self, s):
        s = s.strip()
        if s: self._obj.addItem(s)



class MainWindow(QtGui.QMainWindow):
    """The main window of the TODO application"""

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(600, 400)
        self.setWindowTitle(self.tr('TODO'))
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.createDockWindows()
        self.editWidget = QtGui.QTextEdit()
        self.setCentralWidget(self.editWidget)

        # read settings
        settings = QtCore.QSettings("todo.conf", QtCore.QSettings.IniFormat)
        size = settings.value("MainWindow/Size", QtCore.QSize(800, 600))
        self.resize(size)
        position = settings.value("MainWindow/Position", QtCore.QPoint(10, 10))
        self.move(position)
        # initializing database
        dbName = settings.value("Default/DB_NAME")
        if not dbName:
            dbName = "db/todo.sqlite3"
            settings.setValue( "Default/DB_NAME", dbName )
        dbName = os.path.normpath( os.path.join( APP_DIR, dbName ) )
        dbEncoding = settings.value("Default/DB_ENCODING")
        if not dbEncoding:
            dbEncoding = "utf8"
            settings.setValue( "Default/DB_ENCODING", dbEncoding )
        self.initDb(dbName, dbEncoding)

        self.logger = QCCLog(self.logWidget)
        sys.stdout = sys.stderr = self.logger
        print("stdout: Example error logging")
        sys.stderr.write("stderr: Example error logging")


    def closeEvent(self, event):
        settings = QtCore.QSettings("todo.conf", QtCore.QSettings.IniFormat)
        settings.setValue( "MainWindow/Size", self.size() )
        settings.setValue( "MainWindow/Position", self.pos() )


    def initDb(self, name, encoding):
        """Initializing SQLite database"""
        self.dbName = name
        self.db = SQLite(self.dbName, encoding)


    def createActions(self):
        """Create actions (for menu etc)."""
        self.exitAction = QtGui.QAction(QtGui.QIcon('images/exit.png'), self.tr('Exit'), self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip(self.tr('Exit application'))
        self.aboutAction = QtGui.QAction(self.tr("&About"), self, statusTip=self.tr("Show the application's About box"), triggered=self.about)
        self.aboutQtAction = QtGui.QAction(self.tr("About &Qt"), self, statusTip=self.tr("Show the Qt library's About box"), triggered=QtGui.qApp.aboutQt)
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))


    def createMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(self.tr('&File'))
        fileMenu.addAction(self.exitAction)

        self.viewMenu = menubar.addMenu(self.tr("&View"))

        menubar.addSeparator()

        helpMenu = menubar.addMenu(self.tr("&Help"))
        helpMenu.addAction(self.aboutAction)
        helpMenu.addAction(self.aboutQtAction)


    def createToolBars(self):
        fileToolBar = self.addToolBar("File")
        fileToolBar.setObjectName("FileToolbar")
        fileToolBar.addAction(self.exitAction)


    def createStatusBar(self):
        self.sizeLabel = QtGui.QLabel("     ")
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.sizeLabel.setFrameStyle(QtGui.QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(True)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage(self.tr("Ready"), 5000)


    def createDockWindows(self):
        dockWidget = QtGui.QDockWidget(self.tr("Log"), self)
        dockWidget.setObjectName("LogDockWidget")
        dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|
                                  QtCore.Qt.RightDockWidgetArea)
        self.logWidget = QtGui.QListWidget()
        dockWidget.setWidget(self.logWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
        self.viewMenu.addAction(dockWidget.toggleViewAction())
        # if we don't want to show log widget right away
        # we can uncomment next line:
        #dockWidget.close()


    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About Application"),
                self.tr("The purpose of the <b>Application</b> is to ..."))



if __name__ == "__main__":
    """Main function starting the application.
    To change the style of an application to one of this:
    Plastique, Cleanlooks, CDE, Motif, WindowsXP, Windows
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    from command line:
    todo.py -style CDE
    """
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("images/home.png"))

    QtCore.QTextCodec.setCodecForTr( QtCore.QTextCodec.codecForName("utf8") );
    translator = QtCore.QTranslator()
    translator.load('translations/todo')
    #QtGui.qApp.installTranslator(translator)
    app.installTranslator(translator)

    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

# end of todo.py
