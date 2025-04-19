# -*- coding: utf-8 -*-
{
    'name': "My library",
    'summary': """
        My library summary.
        """,
    'description': """
        Long description of My library.
    """,
    'author': "Serhii Zavalko",
    'website': "https://www.google.com",
    'category': 'Library/Documents',
    'version': '14.0.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'mail'],
    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/res_config_settings.xml',
        'views/library_book.xml',
        'views/res_partner_views.xml',
        'views/library_book_categ.xml',
        'views/library_member.xml',
        'views/library_menu.xml',
        # 'views/demo_model.xml',
        'views/templates.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
