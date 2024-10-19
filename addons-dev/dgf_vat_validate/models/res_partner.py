# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import string
import re
import stdnum
from stdnum.eu.vat import check_vies
from stdnum.exceptions import InvalidComponent
import logging

from odoo import api, models, tools, fields, _
from odoo.tools.misc import ustr
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # ============
    # validate vat.ua
    # ===========
    country_id = fields.Many2one(default=lambda cls: cls.env.ref('base.ua').id)    
    vat_type = fields.Selection(
        [
            ('person', 'ФО'),
            ('company', 'ЮО'),
            ],
        string='Тип коду',
        copy=False,)
    id_type = fields.Selection(
        [
            ("code", "Код"), 
            ("passport", "Паспорт"),
            ("idcard", "ID-картка")
            ],
        string="Тип ідентифікатора",
        copy=False,)
    is_vat_valid = fields.Boolean(string="Код валідовано", default=False)
    # vat_status = fields.Selection(
    #     [("valid", "Коректний"),
    #      ("invalid", "Некоректний"),
    #     ],
    #     string="Статус коду",
    #     copy=False,
    #     default="invalid",
    # )

    def validate_vat(self, code):
        result = {
            'vat': code,
            'id_type': None,
            'vat_type': None,
            'is_vat_valid': False,
        }
        match = re.search(r'^[0-9]+$', code)
        if match:
            result['id_type'] = 'code'
            if len(code) < 8:
                code_filled = code.zfill(8)
            else:
                code_filled = code
            code_len = len(code_filled)
            if code_len == 8:
                result['vat_type'] = 'company'
                if (self.validate_edrpou(code_filled)):
                    result['is_vat_valid'] = True
            elif code_len == 10:
                result['vat_type'] = 'person'
                if (self.validate_rnokpp(code_filled)):
                    result['is_vat_valid'] = True
            result['vat'] = code_filled
            _logger.info(result)

        _logger.info(result)

        return result

    def validate_rnokpp(self, code):
        arrCodeItems = list(code)
        arrIndexes = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
        kSumm = 0

        for i in range(0, len(arrCodeItems) - 1):
            kSumm += int(arrCodeItems[i], 10) * arrIndexes[i]

        kDigit = (kSumm % 11) % 10
        codeKD = int(code[-1], base=10)
        return kDigit == codeKD

    def validate_edrpou(self, code):
        class_1 = {}
        class_1['case_1'] = [1, 2, 3, 4, 5, 6, 7]
        class_1['case_2'] = [3, 4, 5, 6, 7, 8, 9]

        class_2 = {}
        class_2['case_1'] = [7, 1, 2, 3, 4, 5, 6]
        class_2['case_2'] = [9, 3, 4, 5, 6, 7, 8]

        cluster = {}
        cluster['class_1'] = class_1
        cluster['class_2'] = class_2

        codeInt = int(code, base=10)
        if (codeInt > 30000000 and codeInt < 60000000):
            classType = "class_2"
        else:
            classType = "class_1"

        arrIndexes = cluster[classType]
        arrCodeItems = list(code)

        arrIndex = arrIndexes['case_1']
        kSumm = 0

        for i in range(0, len(arrCodeItems) - 1):
            kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]

        kDigit = kSumm % 11

        if kDigit > 9:
            kSumm = 0
            kDigit = 0
            arrIndex = arrIndexes['case_2']
            for i in range(0, len(arrCodeItems) - 1):
                kSumm += int(arrCodeItems[i], base=10) * arrIndex[i]
            kDigit = kSumm % 11
            if kDigit > 9:
                kDigit = 0
        else:
            pass

        codeKD = int(code[-1], base=10)
        return kDigit == codeKD

    def revalidate(self):
        if self.vat:
            result = self.validate_vat(self.vat)
            self.write({
                'is_vat_valid': result['is_vat_valid'],
                'vat': result['vat'],
                'id_type': result['id_type'],
                'vat_type': result['vat_type'],
            })

    # def _fix_vat_number(self, vat, country_id):
    #     code = self.env['res.country'].browse(country_id).code if country_id else False
    #     vat_country, vat_number = self._split_vat(vat)
    #     if code and code.lower() != vat_country:
    #         return vat
    #     stdnum_vat_fix_func = getattr(stdnum.util.get_cc_module(vat_country, 'vat'), 'compact', None)
    #     #If any localization module need to define vat fix method for it's country then we give first priority to it.
    #     format_func_name = 'format_vat_' + vat_country
    #     format_func = getattr(self, format_func_name, None) or stdnum_vat_fix_func
    #     if format_func:
    #         vat_number = format_func(vat_number)
    #     return vat_country.upper() + vat_number

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('vat'):
                result = self.validate_vat(values['vat'])
                values['vat'] = result['vat']
                values['id_type'] = result['id_type']
                values['vat_type'] = result['vat_type']
                values['is_vat_valid'] = result['is_vat_valid']
        return super(ResPartner, self).create(vals_list)

    def write(self, values):
        if values.get('vat'):
            result = self.validate_vat(values['vat'])
            values['vat'] = result['vat']
            values['id_type'] = result['id_type']
            values['vat_type'] = result['vat_type']
            values['is_vat_valid'] = result['is_vat_valid']
        return super(ResPartner, self).write(values)
