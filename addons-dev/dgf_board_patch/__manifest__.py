# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dashboards Patch',
    'version': '1.0',
    'category': 'Liquidation/Productivity',
    'sequence': 225,
    'summary': 'Build your own dashboards',
    'description': """
Lets the user create a custom dashboard.
========================================

Allows users to create custom dashboard.
    """,
    'depends': ['base', 'web', 'board'],
    'data': [
        'views/board_templates.xml',
    ],
    # 'qweb': ['static/src/xml/board.xml'],
    'application': False,
    'license': 'LGPL-3',
}
