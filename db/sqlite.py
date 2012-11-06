#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : sqlite.py
@created : 2012-11-04 00:29:46.091
@changed : 2012-11-06 15:06:12.623
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : module with SQLite utilities
"""
from __future__ import print_function

import os, sys
from argparse import ArgumentParser, Action, SUPPRESS
import threading
from hashlib import md5
import sqlite3

__revision__ = 4


def getRevision():
    """ Callback method for -r/--revision option """
    return str(__revision__)



class Field(object):

    def __init__(self,
                unique      = False,
                notnull     = False,
                default     = None,
                fieldtype   = "text",
                validate    = None,
                displayname = None,
                foreignkey  = None,
                index       = False,
                primary     = False):
        self.coldef = (
                (fieldtype + ' ') +
                ('primary key ' if primary else '') +
                ('unique ' if unique else '') +
                ('not null ' if notnull else '') +
                ('references %s ' % foreignkey if not foreignkey is None else '') +
                ('default %s' % default if not default is None else '')
            ).rstrip()
        self.validate    = validate # check whether this is a function w. 1 arg?
        self.displayname = displayname
        self.foreignkey  = foreignkey
        self.index       = index
        self.primary     = primary



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
        """Reading values from database table into dictionary"""
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


    def existsId(cls, id):
        """Checking existence of id"""
        sql = "select count(*) from {} where {}=?".format( self._tableName, self.idName )
        row = self.db.execSql(sql, (id,))[0]
        return bool(row[0])


    def save(self, id, **args):
        """Saving values from dictionary into database table"""
        if id and self.existsId(id):
            sets = []; vals = []
            for col in args:
                if col!=self._idName and col!='id':
                    sets.append(col + '=?')
                    vals.append(args[col])
            sql = "update {} set {} where {}=?".format(self._tableName, ", ".join(sets), self._idName)
            print(sql)
            vals.append(self._idName)
            cursor = self.db.conn.cursor()
            cursor.execute(sql, vals)
            self.db.conn.commit()
        else:
            for col in args:
                if not col in self._columns:
                    raise KeyError(col + ' is not a valid column')
            if 'id' in args: del args['id']
            cols = ", ".join(args.keys())
            qmarks = ", ".join(['?']*len(args))
            if len(cols):
                sql = "insert into {} ({}) values ({})".format(self._tableName, cols, qmarks)
            else:
                sql = "insert into {} default values".format(self._tableName)
            cursor = self.db.conn.execute(sql, tuple(args.values()))
            self.db.conn.commit()
            if self._idName=='id':
                args["id"] = cursor.lastrowid
            else:
                args["id"] = args[self._idName]
        return args


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



def md5sum(value):
    """ md5 hash of the value """
    return md5(value).hexdigest()



class SQLite(object):
    """ SQLite3 utils """

    def __init__(self, name, encoding='utf8'):
        """ Databse constructor """
        self.name  = name
        self.encoding = encoding
        self._local = threading.local()
        with threading.Lock():
            self._local.conn = sqlite3.connect(name, detect_types=sqlite3.PARSE_DECLTYPES)
            self._local.conn.execute('pragma foreign_keys = 1')
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.create_function("md5", 1, md5sum)
            self._local.conn.text_factory = str


    def __del__(self):
        """ Closing connection on destruction """
        with threading.Lock():
            self._local.conn.close()


    @property
    def conn(self):
        """ Current connection """
        return self._local.conn


    def commit(self):
        """Commits the current transaction"""
        self._local.conn.commit()


    def rollback(self):
        """Roll back any changes to the database
        since the last call to commit()"""
        self._local.conn.rollback()


    def execSql(self, sql, *args):
        """Execution of arbitrary database query.
        Returns the cursor values."""
        return self.conn.execute(sql, *args).fetchall()


    def getIndices(self, table):
        """ List of indexes that defined for a table in the database """
        cursor = self.conn.execute('pragma index_list("%s");' % (table,))
        return sorted([(row[1], row[2] == 1) for row in cursor.fetchall()])


    def getTables(self):
        """ List of tables defined in the database """
        return [row["name"] for row in self.execSql('select name from sqlite_master where type="table" order by name;')]


    def tableExists(self, name):
        """ The existence of a table in a database """
        row = self.execSql('select count(*) as cnt from sqlite_master where type="table" and name=?;', (name,))[0]
        return bool(row["cnt"])


    def getFields(self, table):
        """ The list of fields in the database table """
        cursor = self.conn.execute('pragma table_info("%s");' % (table,))
        columns = [col[1] for col in cursor]
        if not columns:
            raise Exception("No such table")
        return columns


    def getSequences(self):
        """ Sequence list of database tables """
        return [(row["name"], row["seq"]) for row in self.execSql('select * from "sqlite_sequence";')]


    def shrink(self):
        """ Compression and defragmentation of the database """
        sizeBefore = os.path.getsize(self.name)
        self.conn.execute("vacuum")
        sizeAfter  = os.path.getsize(self.name)
        return (sizeBefore, sizeAfter)


    def dump(self, file_name):
        """ Database dump """
        with open(file_name, 'w') as fh:
            for line in self.conn.iterdump():
                fh.write('%s\n' % line)



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

# end of sqlite.py
