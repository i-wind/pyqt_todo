#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : todo.py
@created : 2012-11-04 00:14:14.281
@changed : 2012-11-04 12:48:29.567
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
"""
from __future__ import print_function

import os, sys
from PyQt4 import QtGui, QtCore
from db.sqlite import SQLite
from db.model import Priority, Task
from datetime import datetime, date, timedelta


APP_DIR = os.path.dirname( __file__ )


__version__  = (0, 0, 6)


def getVersion():
    """Version number in string format"""
    return '.'.join(map(str, __version__))



def now():
    """Current date-time"""
    return str(datetime.now())[:-3]



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
        self.setWindowTitle(self.tr('Todo'))
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

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
        debug = settings.value("Default/DEBUG", "False")
        self.debug = False if debug in ("0", "False") else True

        self.createDockWindows()

        self.logger = QCCLog(self.logWidget)
        #sys.stdout = sys.stderr = self.logger

        self.initDb(dbName, dbEncoding)
        if self.debug:
            self.logger.write( "{} database initialized".format(now()) )

        self.createTableWidget()
        self.setCentralWidget(self.tableWidget)


    def closeEvent(self, event):
        settings = QtCore.QSettings("todo.conf", QtCore.QSettings.IniFormat)
        settings.setValue( "MainWindow/Size", self.size() )
        settings.setValue( "MainWindow/Position", self.pos() )


    def initDb(self, name, encoding):
        """Initializing SQLite database"""
        self.dbName = name
        self.db = SQLite(self.dbName, encoding)
        self.priority = Priority(self.db)
        self.task = Task(self.db)
        # for testing purposes
        count = self.db.execSql( "select count(*) from {};".format(self.task.name) )[0][0]
        if count==0:
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                             ("Low Test", 1, date.today() + timedelta(2)) )
            self.db.commit()


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


    def createTableWidget(self):
        """Table widget creation to display TODO lists"""
        self.tableWidget = QtGui.QTableWidget(0, 6)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # select one row at a time
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        # no editing values
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.tableWidget.setHorizontalHeaderLabels((self.tr("ID"), self.tr("Name"), self.tr("Priority"), self.tr("Deadline"),
                                                    self.tr("Completed"), self.tr("Created")))
        #self.tableWidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setShowGrid(True)
        self.refreshTable()


    def refreshTable(self):
        self.tableWidget.setRowCount(0)
        rows = self.db.execSql("select * from TodoTask where completed is null")
        for row in rows:
            cnt = self.tableWidget.rowCount()
            self.tableWidget.insertRow(cnt)
            self.tableWidget.setItem(cnt, 0, QtGui.QTableWidgetItem(str(row["id"])))
            self.tableWidget.setItem(cnt, 1, QtGui.QTableWidgetItem(row["name"]))
            self.tableWidget.setItem(cnt, 2, QtGui.QTableWidgetItem(str(row["priority"])))
            self.tableWidget.setItem(cnt, 3, QtGui.QTableWidgetItem(str(row["deadline"])))
            self.tableWidget.setItem(cnt, 4, QtGui.QTableWidgetItem(str(row["completed"]) if row["completed"] else ""))
            self.tableWidget.setItem(cnt, 5, QtGui.QTableWidgetItem(str(row["created"])))
            QtGui.qApp.processEvents()

        self.tableWidget.resizeColumnsToContents()


    def createDockWindows(self):
        dockWidget = QtGui.QDockWidget(self.tr("Log"), self)
        dockWidget.setObjectName("LogDockWidget")
        dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|
                                  QtCore.Qt.RightDockWidgetArea)
        self.logWidget = QtGui.QListWidget()
        dockWidget.setWidget(self.logWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)
        self.viewMenu.addAction(dockWidget.toggleViewAction())
        if not self.debug: dockWidget.close()


    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About Application"),
                self.tr("The purpose of the <b>Application</b> is:<br>"
                        "&nbsp;&nbsp;&nbsp;&nbsp;- the management of TODO lists..."
                        "<br><br>author: <a href='mailto:qprostu@gmail.com'>Igor A.Vetrov</a> &copy; 2012"
                        "<hr>Version: {}").format(getVersion()))



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
