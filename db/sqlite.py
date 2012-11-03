#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : sqlite.py
@created : 2012-11-04 00:29:46.091
@changed : 2012-11-04 00:29:46.091
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

__revision__ = 1


def getRevision():
    """ Callback method for -r/--revision option """
    return str(__revision__)



def md5sum(value):
    """ md5 hash of the value """
    return md5(value).hexdigest()



class SQLite(object):
    """ SQLite3 utils """

    def __init__(self, name):
        """ Databse constructor """
        self.name  = name
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
