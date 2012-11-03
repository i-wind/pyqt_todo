#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : test_model.py
@created : 2012-11-04 02:28:46.742
@changed : 2012-11-04 03:28:35.538
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : testing application model classes
"""
import os, sys
sys.path.insert( 0, os.path.normpath( os.path.join( os.getcwd(), '..' ) ) )
from db.sqlite import SQLite
from db.model import Priority, Task
import threading
import unittest


__revision__ = 2



class PriorityTable(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.table = Priority(self.db)


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists(self.table.name) )


    def test_low(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (1,) )[0]
        self.assertEqual( row["name"], "Low" )


    def test_medium(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (2,) )[0]
        self.assertEqual( row["name"], "Medium" )


    def test_high(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table.name), (3,) )[0]
        self.assertEqual( row["name"], "High" )



class TaskTable(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.priority = Priority(self.db)
            self.table = Task(self.db)


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists(self.priority.name) )
        self.assertTrue( self.db.tableExists(self.table.name) )



if __name__ == '__main__':

    unittest.main(verbosity=2)

# end of test_model.py
