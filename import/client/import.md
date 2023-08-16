# [Install]
python\python.exe -m pip install --no-index --find-links=z-modules-py odoo_import_export_client

# [Configure]
python\python.exe python\Scripts\odoo_import_thread.py --help
import.conf

# [Use]
python\python.exe python\Scripts\odoo_import_thread.py -c import\client\import.conf --file=import\client\dgf_vp.csv --model=dgf.vp --worker=4 --size=2000

