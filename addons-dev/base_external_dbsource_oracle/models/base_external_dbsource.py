# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import os

from odoo import api
from odoo import models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import oracledb
         # cx_Oracle
        CONNECTORS.append(('oracledb', 'Oracle'))
    except ImportError:
        _logger.info('Oracle libraries not available. Please install '
                     '"oracledb" python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to an Oracle data source. """

    _inherit = "base.external.dbsource"

    PWD_STRING_CX_ORACLE = 'Password=%s;'

    # @api.multi
    def connection_close_oracledb(self, connection):
        return connection.close()

    # @api.multi
    def connection_open_oracledb(self):
        os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'  # explore correct value
        return oracledb.connect(self.conn_string_full)

    # @api.multi
    def execute_oracledb(self, sqlquery, sqlparams, metadata):
        return self._execute_generic(sqlquery, sqlparams, metadata)


# un = 'hr'
# # oracle
# # cs = 'localhost/orclpdb'
# cs = '192.168.56.101/orcl'
# # pw = getpass.getpass(f'Enter password for {un}@{cs}: ')
# pw = 'oracle'
# with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
#     with connection.cursor() as cursor:
#         # sql = """select sysdate from dual"""
#         sql = """select * from hr.countries"""
#         # sql = """SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME FROM HR.EMPLOYEES"""
#         for r in cursor.execute(sql):
#             print(r)