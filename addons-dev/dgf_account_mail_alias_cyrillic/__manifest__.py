# -*- coding: utf-8 -*-
{
    'name': 'DGF: Account Journal Mail Alias Cyrillic',
    'summary': '''DGF: Account Journal Mail Alias Cyrillic''',
    'description': '''DGF: Account Journal Mail Alias Cyrillic''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.0.1',
    'category': 'Liquidation/Configuration',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'mail',
        'account',
    ],
    'external_dependencies': {'python': ['translitua'], 'bin': []},
    'data': [],
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
