@REM echo %~dp0
@echo off

@REM set root=D:\projects\coding\odoo\learn\odoo-book\
@REM set conf=D:\projects\coding\odoo\project\dgf\addons-dgf\
@REM set python=%root%env\Scripts\python.exe
@REM set odoo=%root%src\odoo\odoo-bin
set python=python\python.exe
set odoo=server\odoo-bin
%python% %odoo% -c odoo-win.conf %*