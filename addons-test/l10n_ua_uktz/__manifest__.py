{
    'name': 'Ukraine - UKTZED',
    'version': '14.0.0.0.3',
    'license': 'OPL-1',
    'category': 'Localization',
    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'depends': ['base', 'generic_mixin', ],
    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu_views.xml',
        'views/code_views.xml',
        'views/res_config_settings_view.xml',

        'wizard/upload_uktzed_views.xml',

    ],
    'installable': True,
}
