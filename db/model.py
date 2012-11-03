#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
@script  : model.py
@created : 2012-11-04 01:48:15.090
@changed : 2012-11-04 01:48:15.090
@creator : mkpy.py --version 0.0.27
@author  : Igor A.Vetrov <qprostu@gmail.com>
@about   : model of TODO application
"""
from __future__ import print_function

from argparse import ArgumentParser


__revision__ = 1


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
        if self.name not in self.db.getTables():
            self.db.execSql( __class__.createSql )



if __name__ == '__main__':
    # setup global parser
    parser = ArgumentParser(description='Program description goes here...')
    parser.add_argument('-r', '--revision', action='version', version='%(prog)s revision: ' + getRevision())
    args = parser.parse_args()

# end of model.py
