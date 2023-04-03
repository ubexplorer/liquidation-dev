# [Configure]
python\python.exe server\odoo-bin --data-dir filestore --stop-after-init --save --config odoo.conf
SET "pg_path = C:\Program Files\PostgreSQL\12\bin"
python\python.exe -m pip install --upgrade pip
python\python.exe python\scripts\pip.exe install debugpy
python\python.exe python\scripts\pip.exe install paramiko
python\python.exe python\scripts\pip.exe install py3o.template
python\python.exe python\scripts\pip.exe install py3o.formats
python\python.exe python\scripts\pip.exe install odoo-test-helper

## [Run]
python\python.exe server\odoo-bin --config odoo.conf
RESTORE from bkp
python\python.exe server\odoo-bin --config odoo.conf -d liquidation-dev -u all

python\python.exe -m debugpy --listen 5678 server\odoo-bin --config odoo.conf


