{
    'name': 'Invoice print document for Ukraine',

    'version': '14.0.1.0.3',
    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',
    'license': 'OPL-1',
    'category': 'Accounting',

    'depends': ['account', 'kw_account_partner_requisites', 'product', ],

    'data': [
        'views/account_move_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
