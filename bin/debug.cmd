@REM echo %~dp0
@echo off
set cmd_dir=%~dp0
for %%a in (%cmd_dir:~0,-1%) do set "root=%%~dpa"

set python=%root%env\Scripts\python.exe
set odoo=%root%src\odoo\odoo-bin
@REM %python% %odoo%
%python% -m debugpy --listen 5678 %odoo% -c %root%odoo-win.conf %*