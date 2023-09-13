@REM echo %~dp0
@echo off

@REM set root=D:\projects\coding\odoo\learn\odoo-book\
@REM set conf=D:\projects\coding\odoo\project\dgf\addons-dgf\
@REM set python=%root%env\Scripts\python.exe
@REM set odoo=%root%src\odoo\odoo-bin

@REM set TZ='UTC'
set python=python\python.exe 
set odoo=server\odoo-bin
@REM echo %TZ%
@REM %python% -m debugpy --listen 5678 %odoo% -c odoo-win.conf --log-level=debug %*
%python% -m debugpy --listen 5678 %odoo% -c odoo-win.conf %*
