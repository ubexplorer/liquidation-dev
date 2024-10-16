# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "DGF IAP: Base Provider & http-client",
    "summary": "Base module for providing alternative provider for iap apps",
    "version": "14.0.1.0.0",
    "category": "Liquidation/API",
    "website": "https://github.com/OCA/server-tools",
    "author": "DGF",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["iap"],
    "data": [
        "data/data.xml",
        "views/iap_account_view.xml",
    ],
    "demo": [],
    "qweb": [],
}
