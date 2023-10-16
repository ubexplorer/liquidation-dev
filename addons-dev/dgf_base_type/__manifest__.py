# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base Type Support",
    "summary": "Provides type model and abstract logic for inheritance",
    "version": "14.0.1.0.0",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "category": "base",
    "depends": ["base"],
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/dgf_base_type.xml",
        "views/ir_model_views.xml",
    ],
    "installable": True,
    "application": False,
}
