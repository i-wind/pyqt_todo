#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : model.py
@created : 2012-11-04 01:48:15.090
@changed : 2012-11-05 16:43:09.445
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : model of TODO application
"""
from __future__ import print_function

from argparse import ArgumentParser
from .sqlite import Field


__revision__ = 7
__project__  = "Todo"


def getRevision():
    """Callback method for -r/--revision option"""
    return str(__revision__)



class Table(object):
    """Abstract base model class"""

    _tableName = ""
    _fields    = []
    _idName    = ""
    _columns   = []
    _indices   = []

    def __init__(self, db):
        super(Table, self).__init__()
        self.db = db
        self.__class__._columns = [ k for k, v in self._fields]
        self.__class__._indices = [ k for k, v in self._fields if v.index ]
        self.__class__._idName = "id"
        for k, v in self._fields:
            if v.primary:
                self.__class__._idName = k
                break
        self.checkTable()


    def checkTable(self):
        if self.__class__.__name__=="Table": return
        if self._tableName not in self.db.getTables():
            self.db.execSql( self.createSql() )
            self.db.commit()
            self.setDefaults()
        for i in self._indices:
            sql = "create index if not exists {0}_{1}_index on {0}({1});".format(self._tableName, i)
            self.db.execSql( sql )
            self.db.commit()


    def openId(self, id):
        sql = "select * from {} where {}=?".format(self._tableName, self._idName)
        row = self.db.execSql(sql, (id,))[0]
        if row:
            for col in self._columns:
                setattr(self, col, row[col])
            self.id = id
        else:
            raise AttributeError("id " + str(id) + " does not exists")


    def read(self, id):
        sql = "select * from {} where {}=?".format(self._tableName, self._idName)
        row = self.db.execSql(sql, (id,))[0]
        result = {}
        if row:
            for col in self._columns:
                result[col] = row[col]
            result["id"] = id
        else:
            raise AttributeError("id " + str(id) + " does not exists")
        return result


    def setDefaults(self):
        pass


    def count(self):
        return self.db.execSql( "select count(*) from {};".format(self._tableName) )[0][0]


    def createSql(self):
        sql = ["create table {}(".format(self._tableName),]
        primary = False
        for name, field in self._fields:
            sql.append("\t" + name + " " + field.coldef + ",")
            if field.primary: primary = True
        # delete last ",""
        sql[-1] = sql[-1][:-1]
        sql.append(");")
        if not primary:
            sql.insert(1, "\tid integer primary key autoincrement not null,")
        return "\n".join(sql)



class Priority(Table):
    """Priority model class"""

    _fields = [
        ( "code"   , Field(fieldtype="integer", notnull=True, primary=True) ),
        ( "name"   , Field(notnull=True) ),
        ( "created", Field(fieldtype="timestamp", default="(datetime('now', 'localtime'))") ),
    ]

    def __init__(self, db):
        self.__class__._tableName = __project__ + self.__class__.__name__
        super(Priority, self).__init__(db)


    def setDefaults(self):
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self._tableName), (1, "Low") )
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self._tableName), (2, "Medium") )
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self._tableName), (3, "High") )
        self.db.commit()



class Task(Table):
    """Task model class"""

    _fields = [
        ( "name"     , Field(notnull=True) ),
        ( "priority" , Field(fieldtype="integer", default=2, foreignkey="TodoPriority(code)") ),
        ( "deadline" , Field(fieldtype="date", notnull=True, default="(date('now', 'localtime'))") ),
        # status may be 0 or 1, if 1 - task completed
        ( "status"   , Field(fieldtype="integer", default=0, index=True) ),
        ( "completed", Field(fieldtype="timestamp") ),
        ( "created"  , Field(fieldtype="timestamp", default="(datetime('now', 'localtime'))") ),
    ]

    def __init__(self, db):
        self.__class__._tableName = __project__ + self.__class__.__name__
        super(Task, self).__init__(db)



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

# end of model.py
