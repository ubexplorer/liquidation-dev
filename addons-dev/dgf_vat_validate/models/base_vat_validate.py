# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class BaseVatValidate(models.AbstractModel):
    """
    Validate partner code (vat).
    """
    _name = "base.vat.validate"
    _description = "Vat Validation Abstract"

    vat_type = fields.Selection(
        [
            ('person', 'ФО'),
            ('company', 'ЮО'),
            ],
        string='Тип особи',
        copy=False,)
    id_type = fields.Selection(
        [
            ("code", "Код"), 
            ("passport", "Паспорт"),
            ("idcard", "ID-картка")
            ],
        string="Тип ідентифікатора",
        copy=False,
        default="code")
    vat_status = fields.Selection(
        [("valid", "Коректний"),
         ("invalid", "Некоректний"),
        ],
        string="Статус коду",        
        copy=False,
        default="invalid",
    )

    def _valid_field_parameter(self, field, name):
        # allow tracking on models inheriting from this model
        return name == "tracking" or super()._valid_field_parameter(field, name)

    def validate_vat(self, code):
        result = {
            'vat': code,
            'id_type': None,
            'vat_type': None,
            'vat_status': 'invalid',
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
                    result['vat_status'] = 'valid'                    
            elif code_len == 10:
                result['vat_type'] = 'person'
                if (self.validate_rnokpp(code_filled)):
                    result['vat_status'] = 'valid'
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
                'vat_status': result['vat_status']
            })
