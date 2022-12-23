# -*- coding: utf-8 -*-

# Copyright © 2020 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Regions of Ukraine',
    'version': '14.0.1.0.0',
    'category': 'Localization',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz',
    'license': 'LGPL-3',
    'summary': 'Adds the regions of Ukraine',
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://garazd.biz/r/iVi',
    'description': """
Module adds the regions of Ukraine 
=============================
Список областей з ресурсу: https://uk.wikipedia.org/wiki/Категорія:Області_України
Список кодів областей України згідно КОАТУУ: https://uk.wikipedia.org/wiki/Список_кодів_КОАТУУ_для_областей та https://dovidnyk.in.ua/directories


Технічна підтримка та розробка для системи Odoo
============================================

Контакти для зв`язку з нами:

* support@garazd.biz
* `https://garazd.biz/page/contactus`_
.. _https://garazd.biz/page/contactus: https://garazd.biz/page/contactus

Пакети технічної підтримки: https://garazd.biz/page/odoo-support
    """,
    'depends': [
        'base',
    ],
    'data': [
        'data/res_country_state_data.xml',
    ],
    'external_dependencies': {
    },
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
