# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "ФГВ: Договори",
    "summary": "ФГВ: Договори",
    "version": "14.0.1.1.0",
    "category": "Contract",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "agreement",
        "mail",
        "dgf_base_stage",
        "dgf_base_type"
    ],
    "data": [
        "data/data.xml",
        "data/base_stage.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/agreement_security.xml",
        "views/agreement.xml",
    ],
    "demo": [],
    "development_status": "Beta",
    "maintainers": [
        "ygol",
        "alexis-via",
    ],
    "installable": True,
}
