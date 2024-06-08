# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SMSTemplate(models.Model):
    "Templates for sending SMS"
    _name = "doc.template"
    _inherit = ['mail.render.mixin']
    _description = 'Шаблон документа'

    @api.model
    def default_get(self, fields):
        res = super(SMSTemplate, self).default_get(fields)
        if not fields or 'model_id' in fields and not res.get('model_id') and res.get('model'):
            res['model_id'] = self.env['ir.model']._get(res['model']).id
        return res

    name = fields.Char('Назва', translate=True)
    model_id = fields.Many2one('ir.model', string='Застосовується до', required=True, ondelete='cascade')
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    prefix = fields.Char('Тема документа', required=True)
    body = fields.Html('Основна частина', sanitize=False)
    suffix = fields.Text('Резолютивна частина', required=False)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {},
                       name=_("%s (copy)", self.name))
        return super(SMSTemplate, self).copy(default=default)
