# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "DGF LPD: LPD Client API",
    "summary": "DGF LPD: Клієнтське API ресурсу 'База правових позицій Верховного Суду'",
    "version": "14.0.0.1",
    "category": "Liquidation/API",
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ['dgf_iap_provider'],
    "data": [
        'security/security.xml',
        "views/iap_account_view.xml",
        'data/data.xml',
    ],
    "demo": [],
    "qweb": [],
}
