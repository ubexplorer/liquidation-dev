# -*- coding: utf-8 -*-
{
    'name': 'DGF: hr_timesheet configuration',
    'summary': '''DGF: hr_timesheet configuration''',
    'description': '''DGF: hr_timesheet configuration''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.0.1',
    'category': 'Liquidation/Configuration',
    # any module necessary for this one to work correctly
    'depends': [
        'hr_timesheet',
    ],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'views/hr_timesheet_views.xml',
        'views/project_views.xml',
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
