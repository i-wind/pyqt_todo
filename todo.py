#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : todo.py
@created : 2012-11-04 00:14:14.281
@changed : 2012-11-06 17:18:12.328
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
"""
from __future__ import print_function

import os, sys
from PyQt4 import QtGui, QtCore
from db.sqlite import SQLite
from db.model import Priority, Task
from datetime import datetime, date, timedelta
from ui.dlg_newtask import NewTaskDialog


APP_DIR = os.path.dirname( __file__ )


__version__  = (0, 0, 13)


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
        if self.task.count()==0:
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task.name),
                             ("Low Test", 1, date.today() + timedelta(2)) )
            self.db.commit()


    def createActions(self):
        """Create actions (for menu etc)."""
        self.newTaskAction = QtGui.QAction(QtGui.QIcon('images/editadd.png'),
                self.tr("Add TODO item"), self, shortcut=QtGui.QKeySequence.New,
                statusTip=self.tr("Adding new TODO item"), triggered=self.newTask)
        self.completeAction = QtGui.QAction(QtGui.QIcon('images/editedit.png'),
                self.tr("Complete TODO item"), self, statusTip=self.tr("Completing TODO item"), triggered=self.completeTask)
        self.deleteAction = QtGui.QAction(QtGui.QIcon('images/editdelete.png'),
                self.tr("Delete TODO item"), self, statusTip=self.tr("Deleting TODO item"), triggered=self.deleteTask)
        self.editAction = QtGui.QAction(QtGui.QIcon('images/filenew.png'),
                self.tr("Edit TODO item"), self, shortcut=QtCore.Qt.CTRL|QtCore.Qt.Key_E,
                statusTip=self.tr("Editing TODO item"), triggered=self.editTask)
        self.exitAction = QtGui.QAction(QtGui.QIcon('images/exit.png'), self.tr('Exit'), self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip(self.tr('Exit application'))
        self.aboutAction = QtGui.QAction(QtGui.QIcon('images/about.png'),
                self.tr("&About"), self, statusTip=self.tr("Show the application's About box"), triggered=self.about)
        self.aboutQtAction = QtGui.QAction(QtGui.QIcon('images/qt-logo.png'), self.tr("About &Qt"),
                self, statusTip=self.tr("Show the Qt library's About box"), triggered=QtGui.qApp.aboutQt)
        self.connect(self.exitAction, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))


    def createMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(self.tr('&File'))
        fileMenu.addAction(self.newTaskAction)
        fileMenu.addAction(self.editAction)
        fileMenu.addAction(self.completeAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        self.viewMenu = menubar.addMenu(self.tr("&View"))

        menubar.addSeparator()

        helpMenu = menubar.addMenu(self.tr("&Help"))
        helpMenu.addAction(self.aboutAction)
        helpMenu.addAction(self.aboutQtAction)


    def createToolBars(self):
        taskToolBar = self.addToolBar("Task")
        taskToolBar.setObjectName("TaskToolbar")
        taskToolBar.addAction(self.newTaskAction)
        taskToolBar.addAction(self.editAction)
        taskToolBar.addAction(self.completeAction)

        exitToolBar = self.addToolBar("Exit")
        exitToolBar.setObjectName("ExitToolbar")
        exitToolBar.addAction(self.exitAction)


    def createStatusBar(self):
        self.sizeLabel = QtGui.QLabel("     ")
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.sizeLabel.setFrameStyle(QtGui.QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(True)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage(self.tr("Ready"), 5000)


    def openContextMenu(self, position):
        menu = QtGui.QMenu(self)
        menu.addAction(self.newTaskAction)
        menu.addAction(self.editAction)
        menu.addAction(self.completeAction)
        menu.addSeparator()
        menu.addAction(self.deleteAction)
        #menu.exec_(self.tableWidget.mapToGlobal(position))
        menu.popup(QtGui.QCursor.pos())


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
        #self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        #self.addActions(self.tableWidget, (self.newAction, self.aboutAction))
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.openContextMenu)
        self.tableWidget.cellDoubleClicked.connect(self.rowDblClick)
        self.refreshTable()


    def refreshTable(self):
        self.tableWidget.setRowCount(0)
        rows = self.db.execSql("select * from TodoTask where status=0")
        for row in rows:
            cnt = self.tableWidget.rowCount()
            self.tableWidget.insertRow(cnt)
            self.tableWidget.setItem(cnt, 0, QtGui.QTableWidgetItem(str(row["id"])))
            self.tableWidget.setItem(cnt, 1, QtGui.QTableWidgetItem(row["name"]))
            self.tableWidget.setItem(cnt, 2, QtGui.QTableWidgetItem(self.priority.getName(row["priority"])))
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


    def newTask(self):
        dialog = NewTaskDialog(self)
        dialog.priority.addItems(self.priority.listNames())
        if dialog.exec_():
            args = {}
            args["name"] = dialog.name.text()
            args["priority"] = self.priority.getCode( dialog.priority.currentText() )
            args["deadline"] = dialog.deadline.date().toPyDate()
            args = self.task.save("", **args)
            self.refreshTable()


    def rowDblClick(self, row, col):
        self._updateTask(row)


    def editTask(self):
        # index of currently selected row
        row = self.tableWidget.currentRow()
        if row==-1:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(self.tr('Edit'))
            msgBox.setText(self.tr('Select a task to edit!'))
            msgBox.exec_()
        else:
            self._updateTask(row)


    def _updateTask(self, row):
        # id of currently selected row
        _id = int(self.tableWidget.item(row, 0).text())
        row = self.task.read(_id)
        # open dialog for editing record
        dialog = NewTaskDialog(self)
        dialog.name.setText(row["name"])
        dialog.priority.addItems(self.priority.listNames())
        dialog.priority.setCurrentIndex(row['priority']-1)
        dialog.deadline.setDate(row['deadline'])
        if dialog.exec_():
            row["name"] = dialog.name.text()
            row["priority"] = self.priority.getCode( dialog.priority.currentText() )
            row["deadline"] = dialog.deadline.date().toPyDate()
            args = self.task.save(_id, **row)
            self.refreshTable()


    def completeTask(self):
        # index of currently selected row
        row = self.tableWidget.currentRow()
        if row==-1:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle (self.tr('Complete'))
            msgBox.setText(self.tr('Select a task to complete!'))
            msgBox.exec_()
            return
        # id of currently selected row
        _id = self.tableWidget.item(row, 0).text()
        if QtGui.QMessageBox.question(self, self.tr('Complete'), self.tr('Are you sure to complete this task (id={})?').format(_id),
                                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.db.execSql('update TodoTask set status=1, completed=? where id=?', (datetime.now(), int(_id)))
            self.db.commit()
            self.refreshTable()


    def deleteTask(self):
        # index and id of currently selected row
        row = self.tableWidget.currentRow()
        if row==-1:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle (self.tr('Delete'))
            msgBox.setText(self.tr('Select a task to delete!'))
            msgBox.exec_()
            return
        _id = self.tableWidget.item(row, 0).text()
        if QtGui.QMessageBox.question(self, self.tr('Delete'), self.tr('Are you sure to delete this record (id={})?').format(_id),
                                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            # remove row from table widget
            self.tableWidget.removeRow( row )
            # remove record from database
            self.logger.write( "{} delete from TodoTask where id={}".format(now(), _id) )
            self.db.execSql( 'delete from TodoTask where id=?', (int(_id),) )
            self.db.commit()
            self.statusBar().showMessage('Deleted record id=' + _id, 5000)


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

    # read settings
    settings = QtCore.QSettings("todo.conf", QtCore.QSettings.IniFormat)
    # application internationalization
    lang = settings.value("Default/APP_LANGUAGE")
    del settings
    if lang:
        QtCore.QTextCodec.setCodecForTr( QtCore.QTextCodec.codecForName("utf8") );
        translator = QtCore.QTranslator()
        translator.load("translations/todo_" + lang)
        app.installTranslator(translator)

    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

# end of todo.py
