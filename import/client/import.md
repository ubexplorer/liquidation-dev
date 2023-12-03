# [Install]
python\python.exe -m pip install --no-index --find-links=z-modules-py C

# [Configure]
python\python.exe python\Scripts\odoo_import_thread.py --help
import.conf

# [Use]
python\python.exe python\Scripts\odoo_import_thread.py -c import\client\import.conf --file=import\client\dgf.company.partner.csv --model=dgf.company.partner --worker=4 --size=2000

python\python.exe python\Scripts\odoo_import_thread.py -c import\client\import.conf --file=import\client\dgf.asset.loans.csv --model=dgf.asset --worker=4 --size=2000