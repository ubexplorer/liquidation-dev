# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Заявки щодо активів",
    "summary": "Облік заявок та операцій з активами",
    "version": "14.0.1.1.0",
    "category": "Liquidation/AssetRequest",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "dgf_document",
        "dgf_base_stage",
        # "dgf_base_category",
    ],
    "data": [
        # "security/security.xml",
        "security/ir.model.access.csv",
        "data/base_stage.xml",
        # "data/base_category.xml",
        "views/dgf_request_views.xml",
        "views/dgf_request_menus.xml",
    ],
    "demo": [],
    "installable": True,
    'application': True,
}
