# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import AccessError


class EdrSubject(models.Model):
    _name = 'edr.subject'
    _inherit = [
        'base.stage.abstract',
        'vkursi.api']
    _description = "Суб'єкти в ЄДР"


    @api.model
    def _get_domain(self):
        id = self.env.ref('base.model_res_partner').id
        domain = [('res_model_id', '=', id)]
        return domain

    request_code = fields.Char(string='Код запиту')
    edr_id = fields.Integer(string='ЄДР ID')
    edr_code = fields.Char(string='Код ЄДРПОУ')
    edr_name = fields.Char(string='Повне найменування')
    edr_state_code = fields.Char(string='Код стану')
    edr_state_text = fields.Char(string='Назва стану')
    edr_url = fields.Char(string='URL')
    stage_id = fields.Many2one('base.stage', string='Стан в ЄДР', store=True, ondelete='restrict', tracking=True, index=True,
                                domain=_get_domain,
                                copy=False)
    state = fields.Selection(
        [("relevant", "Актуальний"), ("irrelevant", "Архівний")],
        string="Стан запису",
        required=True,
        copy=False,
        default="irrelevant",
    )
    partner_id = fields.Many2one('res.partner', string='Партнер', required=False, ondelete='restrict', index=True)
    dgf_company_partner_id = fields.Many2one('dgf.company.partner', string='Контрагент банку',required=True, ondelete='restrict', index=True)
    state_datetime = fields.Datetime(string='Оновлено з ЄДР', readonly=True, default=fields.Datetime.now())
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    

    def set_id(self):
        """
        Set EDR subject id to 'dgf.company.partner'.
        """
        print(self.id)
        self.state = 'relevant'
        self.dgf_company_partner_id.edr_id = self.edr_id
        self.dgf_company_partner_id.edr_state_text = self.edr_state_text
        self.dgf_company_partner_id.state_datetime = self.state_datetime
        self.dgf_company_partner_id.fullname = self.edr_name
