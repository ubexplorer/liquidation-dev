# -*- coding: utf-8 -*-

import threading
import logging
from datetime import datetime
from dateutil.parser import parse
# from datetime import timezone
import time

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

# move to edr_subjects
FIELD_MAPPING = {
    'edr_id': 'id',
    'edr_code': 'code',
    'edr_name': 'name',
    'edr_state_code': 'state',
    'edr_state_text': 'state_text',
    'edr_url': 'url'
}


class CompanyPartner(models.Model):
    _inherit = [        
        # 'vkursi.api',
        'dgf.company.partner',
        ]

    # edr_id = fields.Integer(string='ЄДР ID')
    edr_subject_ids = fields.One2many(string="Суб'єкти в ЄДР", comodel_name='edr.subject', inverse_name='dgf_company_partner_id', index=True)

    @api.model
    def _fields_mapping(self, vals):
        """Returns the list of fields that are synced from the parent."""
        fields = dict(FIELD_MAPPING)
        return_dict = {}
        for fk, fv in fields.items():
            field_values = fv.split('/')
            vals_value = vals.get(field_values[0])
            if all([vals_value, not isinstance(vals_value, (dict, list))]):
                if not self.is_date(vals_value):
                    value = vals_value
                else:
                    # value = datetime.strptime(vals_value[:-1], '%Y-%m-%dT%H:%M:%S.%f')  # change approach
                    value = datetime.strptime(vals_value, '%Y-%m-%dT%H:%M:%S.%fZ')
                return_dict[fk] = value
                print(return_dict[fk])
            elif isinstance(vals_value, (dict)):
                return_dict[fk] = vals[field_values[0]][field_values[1]]  # considerr the same logic value as in vals[field_values[0]]
                print(return_dict[fk])

        # print(return_dict)
        return return_dict

    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.
        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        if isinstance(string, str):
            # string = str(string)
            try:
                # sdate = parse(string, fuzzy=fuzzy)
                sdate = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
                if isinstance(sdate, datetime):
                    parse(string, fuzzy=fuzzy)
                    return True
            except ValueError:
                return False
        else:
            return False
    
    def get_freenais_multi_thread(self):
        threaded_method = threading.Thread(
            target=self.get_freenais()
        )
        threaded_method.run()
        id2 = self.env.ref("dgf_iap_vkursi_edr.view_get_freenais_finish").id
        return {
            "binding_view_types": "form",
            "view_mode": "form",
            "res_model": "dgf.company.partner",
            "views": [(id2, "form")],
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }


    @api.model
    def _get_domain(self):
        id = self.env.ref('base.model_res_partner').id
        domain = [('res_model_id', '=', id)]
        return domain

    # ----------------------------------------------------------
    # Vkursi: EDR methods
    # ----------------------------------------------------------
    def get_freenais(self):
        edr_state_text = ''
        sequence = self.env.ref('dgf_iap_vkursi_edr.edr_request_sequence')
        if sequence:
            request_code = sequence.next_by_id()

        provider_name = self.env['iap.account'].get('vkursi')._provider_name        
        responce = self.env['vkursi.api']._api_freenais(code=self.vat, description=provider_name)
        # print(responce)

        if responce is not None and responce['isSuccess']:
            edr_subjects = responce['request_result']
            edr_subject_count = len(edr_subjects)
        
            # переробити логіку обробки помилок
            if edr_subject_count != 0:                
                # неправильна логіка. Переглянути, врахувати стани? exclude -1, 6?
                max_id = max(d['id'] for d in edr_subjects if d['state'] not in [-1, 6])
                # повертати словник, а не скалярне значення
                # max_dict = {k: max(d[k] for d in edr_subjects if d['state'] not in [-1, 6]) for k in edr_subjects[0].keys()}            
                for edr_subject in edr_subjects:
                    edr_subject_fields = self._fields_mapping(edr_subject)
                    edr_subject_fields['partner_id'] = self.partner_id.id
                    edr_subject_fields['request_code'] = request_code

                    edr_stage_id = self.env['base.stage'].search([
                        '&', 
                        ('res_model_id', '=', self.env.ref('base.model_res_partner').id),
                        ('code', '=', str(edr_subject_fields['edr_state_code'])),
                        ], limit=1)              

                    edr_subject_fields['stage_id'] = edr_stage_id.id

                    if edr_subject_fields['edr_id'] == max_id:
                        edr_subject_fields['state'] = 'relevant'
                        edr_state_text = edr_subject_fields['edr_state_text']
                        edr_stage = edr_subject_fields['stage_id']
                        fullname = edr_subject_fields['edr_name']
                        state_datetime = fields.Datetime.now()
                    # else:
                    #     edr_subject_fields['state'] = 'irrelevant'
                    
                    # print(edr_subject_fields)
                    self.write({'edr_subject_ids': [(0, 0, edr_subject_fields)]})                
                self.write({
                    'edr_id': max_id,
                    'edr_state_text': edr_state_text,
                    'stage_id': edr_stage,
                    'fullname': fullname,
                    'edr_subject_count': edr_subject_count,
                    'state_datetime': state_datetime,
                    })
                self.env.cr.commit()  # commit every record
            else:
                self.write({
                    'edr_state_text': 'дані відсутні',
                    })
                self.env.cr.commit()  # commit every record

            time.sleep(0.5)

    def get_paynaissign(self):
        provider_name = self.env['iap.account'].get('vkursi')._provider_name
        response = self.api_getadvancedorganization(code=self.vat, description=provider_name)
        print(response)
        #  analyse errors with responce
        # json_data = json.loads(responce)
        request_result = response['request_result']
        request_datetime = response['request_datetime']
        if response['isSuccess']:
            data = response['data'],
            edr_state = data['state_text'] if data['state_text'] is not None else False,
            # 'edr_id': data['id'],
            # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            # 'edr_last_sign': response['sign'],
            # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
        else:
            edr_state = False

        self.write({
            'request_result': request_result,
            'request_datetime': request_datetime,
            'edr_state': edr_state,
            # 'edr_id': data['id'],
            # 'edr_last_responce': json.dumps(data, ensure_ascii=False).encode('utf8'),
            # 'edr_last_sign': response['sign'],
            # 'comment': json.dumps(response, ensure_ascii=False).encode('utf8'),
        })
        self.env.cr.commit()
        time.sleep(5)
