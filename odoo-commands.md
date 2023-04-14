# [Configure]
## Windows
python\python.exe server\odoo-bin --data-dir filestore --stop-after-init --save --config odoo.conf
SET "pg_path = C:\Program Files\PostgreSQL\12\bin"
python\python.exe -m pip install --upgrade pip
python\python.exe python\scripts\pip.exe install debugpy
python\python.exe python\scripts\pip.exe install paramiko
python\python.exe python\scripts\pip.exe install py3o.template
python\python.exe python\scripts\pip.exe install py3o.formats
python\python.exe python\scripts\pip.exe install odoo-test-helper

## [Run]
### Windows
python\python.exe server\odoo-bin --config odoo.conf
bin\odoo

sudo netstat -tulpn

### RESTORE from bkp
python\python.exe server\odoo-bin --config odoo.conf -d liquidation-dev -u all

python\python.exe -m debugpy --listen 5678 server\odoo-bin --config odoo.conf

## [Run from another user in Ubuntu: `odoo`]
sudo -H -u odoo bash -c '/usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --logfile None'
sudo -H -u odoo bash -c '/usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --logfile None --database liquidation --update all'

[OR]
sudo su - odoo -s /bin/bash
/usr/bin/python3 /usr/bin/odoo --config /etc/odoo/odoo.conf --database liquidation --update all