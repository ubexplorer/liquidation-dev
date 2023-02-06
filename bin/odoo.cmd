@REM echo %~dp0
@echo off
set cmd_dir=%~dp0
for %%a in (%cmd_dir:~0,-1%) do set "root=%%~dpa"
@REM echo %root%

@REM set root=%~dp0/..

@REM SET mypath=%~dp0
@REM echo %mypath:~0,-1%

set python=%root%env\Scripts\python.exe
set odoo=%root%src\odoo\odoo-bin
@REM %python% %odoo%
%python% %odoo% -c %root%odoo-win.conf %*