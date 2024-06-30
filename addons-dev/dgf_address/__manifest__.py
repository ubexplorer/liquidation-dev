{
    'name': 'Address',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '14.0.1.0.2',
    'depends': [
        'base',
        'l10n_ua_address'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu_view.xml',
        'views/address_type_views.xml',
        'views/address_views.xml',

    ],
    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
