# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Заявки щодо активів",
    "summary": "Облік заявок та операцій з активами",
    "version": "14.0.1.1.0",
    "category": "Liquidation/Task",
    "author": "DGF",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "project",
        "dgf_document",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/dgf_task_views.xml",
        "views/dgf_task_menus.xml",
    ],
    "demo": [],
    "installable": True,
    'application': True,
}
