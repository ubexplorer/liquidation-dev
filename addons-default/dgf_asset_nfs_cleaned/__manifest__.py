{
    "name": "МНП (Знеособлений)",
    "summary": "Майно, що не підлягає продажу (Знеособлений перелік)",
    "version": "14.0.1.1.0",
    "category": "Liquidation/AssetsNFS",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "dgf_asset_nfs",
        "dgf_asset_blocked",
        ],
    "data": [
        "security/ir.model.access.csv",
        "views/asset_nfs_item_united_views.xml",
    ],
    "demo": [],
    "development_status": "Beta",
    "maintainers": [
        "ygol",
        "alexis-via",
    ],
    "installable": True,
    'application': False,
}
