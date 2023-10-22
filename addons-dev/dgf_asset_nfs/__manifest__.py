# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Майно не для продажу",
    "summary": "Операції з майном, що не підлягає продажу",
    "version": "14.0.1.1.0",
    "category": "Liquidation/AssetsNFS",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "dgf_insolvent",
        "dgf_document",
        "dgf_base_stage",
        "dgf_base_type",
        "dgf_base_request",
        "dgf_help_article",
        "attachment_category"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/help_article.xml",
        "data/base_stage.xml",
        "data/base_type.xml",
        "data/base_category.xml",
        # "views/ir_attachment_views.xml",
        "views/asset_nfs_list_item.xml",
        "views/asset_nfs_list.xml",
        "views/asset_nfs_request_views.xml",
        "views/res_company_views.xml",
        'views/help_article_views.xml',
        "views/asset_nfs_menus.xml",
    ],
    "demo": [],
    "development_status": "Beta",
    "maintainers": [
        "ygol",
        "alexis-via",
    ],
    "installable": True,
    'application': True,
}
