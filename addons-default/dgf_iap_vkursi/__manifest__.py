# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "DGF: Vkursi IAP",
    "summary": "Vkursi HTTP API",
    "version": "14.0.0.1",
    "category": "Liquidation/API",
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
        "views/res_partner_views.xml",
    ],
    "demo": [],
    "qweb": [],
}
