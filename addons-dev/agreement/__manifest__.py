# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Agreement",
    "summary": "Adds an agreement object",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "dgf_base_stage",
        ],
    "data": [
        "security/ir.model.access.csv",
        "security/agreement_security.xml",
        "data/base_stage.xml",
        "views/agreement.xml",
        "views/agreement_type.xml",
    ],
    "demo": ["demo/demo.xml"],
    "development_status": "Beta",
    "maintainers": [
        "ygol",
        "alexis-via",
    ],
    "installable": True,
}
