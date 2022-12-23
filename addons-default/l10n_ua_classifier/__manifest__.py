# -*- coding: utf-8 -*-
{
    'name': 'DGF: Classifier',
    'summary': '''DGF: Classifier''',
    'description': '''DGF: Classifier''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.1',
    'category': 'Liquidation/Taxonomy',
    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],
    'external_dependencies': {'python': [], 'bin': []},
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stat_classifier_views.xml',
        'views/stat_classifier_item_views.xml',
        'views/stat_classifier_menu.xml',
    ],
    'demo': [],
    'qweb': [],
    'post_load': None,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
    'auto_install': False,
    'application': False,
    'installable': True,
}
