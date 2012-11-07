#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : test_model.py
@created : 2012-11-04 02:28:46.742
@changed : 2012-11-08 01:47:58.385
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
from datetime import datetime, date, timedelta
from sqlite3 import IntegrityError


__revision__ = 10



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
        self.assertTrue( self.db.tableExists(self.table._tableName) )


    def test_create_sql(self):
        sql = "create table TodoPriority(\n" \
              "\tcode integer primary key not null,\n" \
              "\tname text not null,\n" \
              "\tcreated timestamp default (datetime('now', 'localtime'))\n" \
              ");"
        self.assertEqual( sql, self.table.createSql() )


    def test_count(self):
        cnt = self.table.count()
        self.assertEqual( cnt, 3 )


    def test_id_name(self):
        self.assertEqual( self.table._idName, "code" )


    def test_low(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table._tableName), (1,) )[0]
        self.assertEqual( row["name"], "Low" )


    def test_medium(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table._tableName), (2,) )[0]
        self.assertEqual( row["name"], "Medium" )


    def test_high(self):
        row = self.db.execSql( "select name from {} where code=?;".format(self.table._tableName), (3,) )[0]
        self.assertEqual( row["name"], "High" )


    def test_openId(self):
        self.table.openId(1) 
        self.assertEqual( self.table.name, "Low" )


    def test_read(self):
        args = self.table.read(2)
        self.assertEqual( args["code"], 2 )
        self.assertEqual( args["name"], "Medium" )
        self.assertEqual( args["id"], 2 )


    def test_save(self):
        args = dict(code=9, name="Unused")
        args = self.table.save("", **args)
        self.assertEqual( self.table.count(), 4 )
        self.assertEqual( args["id"], 9 )
        del args
        args = self.table.read(9)
        self.assertEqual( args["id"], 9 )
        self.assertEqual( args["code"], 9 )
        self.assertEqual( args["name"], "Unused" )


    def test_update(self):
        args = dict(code=9, name="Unused")
        args = self.table.save("", **args)
        del args
        args = self.table.read(9)
        args["name"] = "Used"
        args = self.table.save(9, **args)
        del args
        args = self.table.read(9)
        self.assertEqual( args["id"], 9 )
        self.assertEqual( args["code"], 9 )
        self.assertEqual( args["name"], "Used" )


    def test_delete(self):
        args = self.table.deleteId(2)
        self.assertEqual( self.table.count(), 2 )
        self.assertFalse( self.table.existsId(2) )


    def test_getValue(self):
        value = self.table.getValue(2, "name")
        self.assertEqual( value, "Medium" )



class TaskTable(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.priority = Priority(self.db)
            self.task = Task(self.db)
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task._tableName),
                             ("Low Test", 1, date.today() + timedelta(2)) )
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task._tableName),
                             ("Medium Test", 2, date.today() + timedelta(3)) )
            self.db.execSql( "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task._tableName),
                             ("High Test", 3, date.today() + timedelta(4)) )


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists(self.priority._tableName) )
        self.assertTrue( self.db.tableExists(self.task._tableName) )


    def test_create_sql(self):
        sql = "create table TodoTask(\n" \
              "\tid integer primary key autoincrement not null,\n" \
              "\tname text not null,\n" \
              "\tpriority integer references TodoPriority(code) default 2,\n" \
              "\tdeadline date not null default (date('now', 'localtime')),\n" \
              "\tstatus integer default 0,\n" \
              "\tcompleted timestamp,\n" \
              "\tcreated timestamp default (datetime('now', 'localtime'))\n" \
              ");"
        self.assertEqual( sql, self.task.createSql() )


    def test_index_exists(self):
        self.assertIn( "status", self.task._indices )


    def test_id_name(self):
        self.assertEqual( self.task._idName, "id" )


    def test_count(self):
        cnt = self.task.count()
        self.assertEqual( cnt, 3 )


    def test_low(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task._tableName), (1,) )[0]
        self.assertEqual( row["name"], "Low Test" )
        self.assertEqual( row["priority"], 1 )
        self.assertEqual( row["deadline"], date.today() + timedelta(2) )


    def test_medium(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task._tableName), (2,) )[0]
        self.assertEqual( row["name"], "Medium Test" )
        self.assertEqual( row["priority"], 2 )
        self.assertEqual( row["deadline"], date.today() + timedelta(3) )


    def test_high(self):
        row = self.db.execSql( "select * from {} where id=?;".format(self.task._tableName), (3,) )[0]
        self.assertEqual( row["name"], "High Test" )
        self.assertEqual( row["priority"], 3 )
        self.assertEqual( row["deadline"], date.today() + timedelta(4) )


    def test_integrity(self):
        self.assertRaises( IntegrityError, self.db.execSql,
                           "insert into {} (name, priority, deadline) values(?, ?, ?)".format(self.task._tableName),
                           ("Highest Test", 4, date.today() + timedelta(4)) )


    def test_openId(self):
        self.task.openId(2) 
        self.assertEqual( self.task.name, "Medium Test" )


    def test_read(self):
        args = self.task.read(2)
        self.assertEqual( args["id"], 2 )
        self.assertEqual( args["name"], "Medium Test" )
        self.assertEqual( args["priority"], 2 )
        self.assertEqual( args["deadline"], date.today() + timedelta(3) )


    def test_save(self):
        args = dict(name="Highest Test", priority=3, deadline=date.today()+timedelta(5))
        args = self.task.save("", **args)
        self.assertEqual( self.task.count(), 4 )
        self.assertEqual( args["id"], 4 )
        del args
        args = self.task.read(4)
        self.assertEqual( args["id"], 4 )
        self.assertEqual( args["status"], 0 )
        self.assertEqual( args["name"], "Highest Test" )
        self.assertEqual( args["priority"], 3 )
        self.assertEqual( args["deadline"], date.today() + timedelta(5) )


    def test_delete(self):
        args = self.task.deleteId(3)
        self.assertEqual( self.task.count(), 2 )
        self.assertFalse( self.task.existsId(3) )


    def test_getValue(self):
        value = self.task.getValue(3, "name")
        self.assertEqual( value, "High Test" )



if __name__ == '__main__':

    unittest.main(verbosity=2)

# end of test_model.py
