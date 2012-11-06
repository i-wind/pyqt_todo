#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : model.py
@created : 2012-11-04 01:48:15.090
@changed : 2012-11-06 15:06:02.890
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : model of TODO application
"""
from __future__ import print_function

from argparse import ArgumentParser
from .sqlite import Table, Field


__revision__ = 9
__project__  = "Todo"


def getRevision():
    """Callback method for -r/--revision option"""
    return str(__revision__)



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
