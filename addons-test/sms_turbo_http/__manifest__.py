# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sms TurboSMS HTTP",
    "summary": "Send sms using ovh TurboSMS API",
    "version": "14.0.1.0.3",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "base_phone",
        "sms",
        "mass_mailing_sms",
        "dgf_iap_provider",
        # 'dgf_asset',
    ],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_sms_view.xml",
        "views/mailing_mailing_views.xml",
        "views/mailing_sms_menus.xml"
    ],
    "demo": [],
    "qweb": [],
}
