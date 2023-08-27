# [Install]
python\python.exe -m pip install --no-index --find-links=z-modules-py odoo_import_export_client

# [Configure]
python\python.exe python\Scripts\odoo_import_thread.py --help
import.conf

# [Use]
python\python.exe python\Scripts\odoo_import_thread.py -c import\client\import.conf --file=import\client\dgf.company.partner.test.csv --model=dgf.company.partner --worker=4 --size=2000

python\python.exe python\Scripts\odoo_import_thread.py -c import\client\import.conf --file=import\client\dgf.asset.loans.test.csv --model=dgf.asset --worker=4 --size=2000