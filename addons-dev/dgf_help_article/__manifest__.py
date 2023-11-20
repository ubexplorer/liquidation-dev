# -*- coding: utf-8 -*-
{
    'name': 'Статті довідки',
    'summary': '''Статті довідки''',
    'description': '''Статті довідки''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.1',
    'category': 'Liquidation/Help',
    'depends': [
        'base',
        'mail',
        'web'],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/help_article_views.xml', 

    ],
    # 'demo': [],
    # 'qweb': [],
    # 'post_load': None,
    # 'pre_init_hook': None,
    # 'post_init_hook': None,
    # 'uninstall_hook': None,
    'auto_install': False,
    'application': False,
    'installable': True,
}
