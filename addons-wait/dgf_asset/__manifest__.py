# -*- coding: utf-8 -*-
{
    'name': 'DGF: Assets',
    'summary': '''DGF Assets module''',
    'description': '''DGF Assets module''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.1',
    'category': 'Liquidation/Assets',
    'depends': [
        'base',
        'mail',
        'web',
        'contacts',
        # 'dgf_board_patch',
        'dgf_base_stage',
        'dgf_insolvent',
        'l10n_ua_classifier'],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'security/groups.xml',
        'security/security_rules.xml',
        # 'views/res_config_settings.xml',
        'security/ir.model.access.csv',
        'data/dgf_asset_category.xml',
        'data/base_stage.xml',
        # 'data/dgf.asset.category.csv',
        'data/dgf.asset.register.type.csv',
        'data/mail_data.xml',
        'views/dgf_asset_category_views.xml',
        'views/ir_attachment_views.xml',
        'views/dgf_asset_views.xml',
        'views/dgf_company_partner_views.xml',
        'views/res_partner_views.xml',
        # 'views/dgf_asset_loan_views.xml',
        'views/dgf_asset_menus.xml',
        # 'views/board_views.xml',
    ],
    # 'demo': [],
    # 'qweb': [],
    # 'post_load': None,
    # 'pre_init_hook': None,
    # 'post_init_hook': None,
    # 'uninstall_hook': None,
    'auto_install': False,
    'application': True,
    'installable': True,
}