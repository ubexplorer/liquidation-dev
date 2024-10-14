# -*- coding: utf-8 -*-

{
    'name': 'Валідація коду (vat) контрагента',
    'version': '1.0',
    'category': 'Liquidation/Validation',
    'description': """Валідація коду (vat) контрагента.""",
    'depends': [
        'base',
        'dgf_asset_base'],    
    'data': [
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/dgf_company_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'license': 'LGPL-3',
}
