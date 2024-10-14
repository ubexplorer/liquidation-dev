# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Майно блоковане",
    "summary": "Операції з майном, що блокується",
    "version": "14.0.1.1.0",
    "category": "Liquidation/AssetsBlocked",
    "author": "Akretion, "
    "Yves Goldberg (Ygol Internetwork), "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "dgf_insolvent",
        "dgf_document",
        "dgf_base_stage",
        "dgf_base_type",
        "dgf_help_article",
        "report_py3o",        
        "attachment_category"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/help_article.xml",
        "data/base_stage.xml",
        "data/base_type.xml",
        "views/ir_attachment_views.xml",
        "views/dgf_base_type.xml",
        "views/asset_blocked_list_item.xml",
        "views/asset_blocked_list.xml",        
        "views/asset_blocked_subject_views.xml",
        "views/asset_blocked_document_views.xml",
        "views/dgf_document_blocked_views.xml",
        "views/asset_blocked_agreement_views.xml",
        "views/asset_blocked_request_views.xml",
        "views/res_company_views.xml",
        'views/help_article_views.xml',
        'views/mail_activity_views.xml',
        "views/asset_blocked_menus.xml",
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
