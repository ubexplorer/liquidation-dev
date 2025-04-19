import getpass

import oracledb

un = 'hr'
# oracle
# cs = 'localhost/orclpdb'
cs = '192.168.56.101/orcl'
# pw = getpass.getpass(f'Enter password for {un}@{cs}: ')
pw = 'oracle'
with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
    with connection.cursor() as cursor:
        # sql = """select sysdate from dual"""
        sql = """select * from hr.countries"""
        # sql = """SELECT EMPLOYEE_ID, FIRST_NAME, LAST_NAME FROM HR.EMPLOYEES"""
        for r in cursor.execute(sql):
            print(r)