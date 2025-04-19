# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
# import re

from odoo import api, fields, models, tools, _
# from odoo.exceptions import UserError, ValidationError
# from odoo.osv import expression
# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class Classifier(models.Model):
    _inherit = "stat.classifier"

    def classifiers_get(self):
        responce = self.env['prozorro.api']._classifiers_get(
            code=self.code, description='Prozorro API')
        if responce is not None:
            items = self.env['stat.classifier.item']
            vals = []
            # data = {}
            for key, value in responce.items():
                data = {
                    'classifier_id': self.id,
                    'code': key,
                    'name': value['uk_UA'],
                    'full_name': value['uk_UA']
                }
                vals.append(data)
                print(data)

            items.create(vals)
            result = True
        else:
            result = False
        # time.sleep(3)
        return result
