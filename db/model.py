#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : model.py
@created : 2012-11-04 01:48:15.090
@changed : 2012-11-04 18:48:27.550
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : model of TODO application
"""
from __future__ import print_function

from argparse import ArgumentParser
from .sqlite import Field


__revision__ = 5
__project__  = "Todo"


def getRevision():
    """Callback method for -r/--revision option"""
    return str(__revision__)



class Table(object):
    """Abstract base model class"""

    _fields = []

    def __init__(self, db):
        super(Table, self).__init__()
        self.db = db
        self.columns = [ k for k, v in self._fields]
        self.indices = [ k for k, v in self._fields if v.index ]
        self.checkTable()


    def checkTable(self):
        if self.__class__.__name__=="Table": return
        if self.name not in self.db.getTables():
            self.db.execSql( self.createSql() )
            self.db.commit()
            self.setDefaults()
        if self.indices:
            for i in self.indices:
                sql = "create index if not exists {0}_{1}_index on {0}({1});".format(self.name, i)
                self.db.execSql( sql )
                self.db.commit()


    def setDefaults(self):
        pass


    def count(self):
        return self.db.execSql( "select count(*) from {};".format(self.name) )[0][0]


    def createSql(self):
        sql = ["create table {}(".format(self.name),]
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
        self.name = __project__ + self.__class__.__name__
        super(Priority, self).__init__(db)


    def setDefaults(self):
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self.name), (1, "Low") )
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self.name), (2, "Medium") )
        self.db.execSql( "insert into {} (code, name) values(?, ?)".format(self.name), (3, "High") )
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
        self.name = __project__ + self.__class__.__name__
        super(Task, self).__init__(db)



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

# end of model.py
