# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Vkursi: EDR API",
    "summary": "Vkursi HTTP API",
    "version": "14.0.0.1",
    "category": "Liquidation/API",
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ['dgf_iap_vkursi', 'contacts'],
    "data": [
        # 'security/security.xml',
        # "views/iap_account_view.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
    ],
    "demo": [],
    "qweb": [],
}
