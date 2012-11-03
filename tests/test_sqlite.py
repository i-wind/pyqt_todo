#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : test_sqlite.py
@created : 2012-11-04 00:37:17.123
@changed : 2012-11-04 00:37:17.123
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : testing SQLite module
"""
import os, sys
sys.path.insert( 0, os.path.normpath( os.path.join( os.getcwd(), '..' ) ) )
from db.sqlite import SQLite
import threading
import unittest


__revision__ = 1



class SQLiteDatabase(unittest.TestCase):

    def setUp(self):
        with threading.Lock():
            self.dbName = "test.sqlite3"
            self.db = SQLite(self.dbName)
            self.createTable()


    def tearDown(self):
        with threading.Lock():
            if os.path.exists(self.dbName):
                self.db.__del__()
                os.unlink(self.dbName)


    def createTable(self):
        self.db.execSql( """create table if not exists test (
            id integer primary key autoincrement not null,
            user_id text unique not null);"""
        )


    def dropTable(self):
        self.db.execSql("drop table if exists test;")


    def test_tables(self):
        self.assertIn( "test", self.db.getTables() )


    def test_exec_sql(self):
        self.dropTable()
        self.assertNotIn( "test", self.db.getTables() )
        self.createTable()
        self.assertIn( "test", self.db.getTables() )
        self.dropTable()
        self.assertNotIn( "test", self.db.getTables() )


    def test_table_exists(self):
        self.assertTrue( self.db.tableExists("test") )
        self.assertFalse( self.db.tableExists("try_test") )


    def test_columns(self):
        cols = self.db.getFields("test")
        self.assertEqual( ["id", "user_id"], cols )


    def test_indices(self):
        indices = self.db.getIndices("test")
        self.assertEqual( [('sqlite_autoindex_test_1', True)], indices )
        self.db.execSql("create index test_user_id on test(user_id);")
        indices = self.db.getIndices("test")
        self.assertEqual( [('sqlite_autoindex_test_1', True), ('test_user_id', False)], indices )


    def test_sequences(self):
        result = self.db.execSql( "insert into test (user_id) values ('orlmon');" )
        self.assertIn( ("test", 1), self.db.getSequences() )


    def test_insert(self):
        result = self.db.execSql( "insert into test (user_id) values ('orlmon');" )
        self.assertEqual( [], result )
        self.db.execSql( "insert into test (user_id) values ('orlpuv');" )
        self.db.execSql( "insert into test (user_id) values ('orljuk');" )
        rows = self.db.execSql("select count(*) from test;")
        # rows = [(3,)]
        self.assertEqual( 3, rows[0][0] )


    def test_executemany(self):
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',), ('orltest',)] )
        row = self.db.execSql("select count(*) as cnt from test;")[0]
        self.assertEqual( 4, row['cnt'] )


    def test_select(self):
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        row = self.db.execSql( "select user_id from test where id=?;", (2,) )[0]
        # row = ('orlpuv',)
        self.assertEqual( "orlpuv", row['user_id'] )


    def test_update(self):
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        row = self.db.execSql( "select user_id from test where id=?;", (2,) )[0]
        self.assertEqual( "orlpuv", row["user_id"] )
        result = self.db.execSql( "update test set user_id='orldrz' where id=?;", (2,) )
        self.assertEqual( [], result )
        row = self.db.execSql( "select user_id from test where id=?;", (2,) )[0]
        self.assertEqual( "orldrz", row["user_id"] )


    def test_rollback(self):
        self.db.execSql( "insert into test (user_id) values ('orlmon');" )
        self.db.execSql( "insert into test (user_id) values ('orlpuv');" )
        self.db.execSql( "insert into test (user_id) values ('orljuk');" )
        self.db.rollback()
        row = self.db.execSql( "select count(*) from test;" )[0]
        self.assertEqual( 0, row[0] )
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        row = self.db.execSql( "select id from test where user_id=?;", ('orljuk',) )[0]
        self.assertEqual( 3, row[0] )
        self.db.rollback()
        row = self.db.execSql( "select count(*) from test;" )[0]
        self.assertEqual( 0, row[0] )
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        self.db.commit()
        self.db.rollback()
        row = self.db.execSql( "select id from test where user_id=?;", ('orlpuv',) )[0]
        self.assertEqual( 2, row[0] )


    def test_shrink(self):
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        for i in range(1000):
            self.db.execSql( "insert into test (user_id) values ('orltst_%d');" % i )
        self.db.commit()
        self.db.execSql( "delete from test where user_id like ('orltst%');" )
        self.db.commit()
        self.assertEqual( (41984, 4096), self.db.shrink() )


    def test_dump(self):
        dump = """BEGIN TRANSACTION;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('test',3);
CREATE TABLE test (
            id integer primary key autoincrement not null,
            user_id text unique not null);
INSERT INTO "test" VALUES(1,'orlmon');
INSERT INTO "test" VALUES(2,'orlpuv');
INSERT INTO "test" VALUES(3,'orljuk');
COMMIT;
"""
        self.db.conn.executemany( "insert into test (user_id) values (?)", [('orlmon',), ('orlpuv',), ('orljuk',)] )
        dumpName = "{}.dump".format(self.db.name.split(".")[0])
        self.db.dump( dumpName )
        try:
            with open(dumpName, "r") as fh:
                self.assertEqual( dump, fh.read() )
        finally:
            if os.path.exists(dumpName):
                os.unlink(dumpName)


    def test_md5(self):
        value = self.db.conn.execute("select md5(?)", (b"testing",)).fetchone()[0]
        self.assertEqual( value, 'ae2b1fca515949e5d54fb22b8ed95575' )
        #self.assertRaises( sqlite3.OperationalError, self.db.conn.execute, "select md5(?)", ("testing",) )

# end of class SQLiteDatabase(unittest.TestCase):



if __name__ == '__main__':
    unittest.main(verbosity=2)

# end of test_sqlite.py
