{
    "name": "Базові запити: розширення - Майно не для продажу",
    "summary": "Операції з майном, що не підлягає продажу, консолідовані у базових запитах.",
    "version": "14.0.1.1.0",
    "category": "Liquidation/AssetsNFS",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "dgf_base_request",
        "dgf_asset_nfs",
    ],
    "data": [
        "data/base_category.xml",
        "views/asset_nfs_request_views.xml",
        "views/asset_nfs_menus.xml",

    ],
    "demo": [],
    "development_status": "Beta",
    "installable": True,
    'application': False,
    'auto_install': False,
}
