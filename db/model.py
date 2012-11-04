#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : model.py
@created : 2012-11-04 01:48:15.090
@changed : 2012-11-04 12:50:45.823
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : model of TODO application
"""
from __future__ import print_function

from argparse import ArgumentParser


__revision__ = 4
__project__  = "Todo"


def getRevision():
    """Callback method for -r/--revision option"""
    return str(__revision__)



class Table(object):
    """Abstract base model class"""

    def __init__(self, db):
        super(Table, self).__init__()
        self.db = db
        self.checkTable()


    def checkTable(self):
        if self.__class__.__name__=="Table": return
        if self.name not in self.db.getTables():
            self.db.execSql( self.createSql )
            self.db.commit()
            self.setDefaults()


    def setDefaults(self):
        pass


    def count(self):
        return self.db.execSql( "select count(*) from {};".format(self.name) )[0][0]



class Priority(Table):
    """Priority model class"""

    createSql = "create table TodoPriority(" \
                "code integer primary key, " \
                "name text not null, " \
                "created timestamp default (datetime('now', 'localtime')));"

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

    createSql = "create table TodoTask(" \
                "id integer primary key autoincrement not null, " \
                "name text not null, " \
                "priority integer references TodoPriority(code) default 2, " \
                "deadline date not null default (date('now', 'localtime')), " \
                "completed timestamp, " \
                "created timestamp default (datetime('now', 'localtime')));"

    def __init__(self, db):
        self.name = __project__ + self.__class__.__name__
        super(Task, self).__init__(db)



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

# end of model.py
