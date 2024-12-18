# -*- coding: utf-8 -*-
{
    'name': 'DGF: Auction',
    'summary': '''DGF Auction module''',
    'description': '''DGF Auction module''',
    'author': 'DGF',
    'website': 'https://fg.gov.ua',
    'license': 'AGPL-3',
    'version': '14.0.0.1',
    'category': 'Liquidation/Auction',
    'depends': [
        # 'base',
        # 'mail',
        'dgf_iap_provider',
        # 'dgf_asset',
        'dgf_document',
        'l10n_ua_classifier'],
    'external_dependencies': {'python': [], 'bin': []},
    'data': [
        'data/cron.xml',
        'data/data.xml',
        'security/groups.xml',
        # 'security/security_rules.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/dgf_auction_views.xml',
        'views/dgf_auction_category_views.xml',
        'views/dgf_auction_lot_views.xml',
        'views/dgf_auction_lot_asset_views.xml',
        # 'views/dgf_asset_views.xml',
        'views/stat_classifier_views.xml',
        'views/dgf_auction_menus.xml',
        'views/res_config_settings.xml',
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
