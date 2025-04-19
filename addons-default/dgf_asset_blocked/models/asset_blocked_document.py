# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import unquote


class AssetBlockedDocument(models.Model):
    _name = 'asset.blocked.document'
    _description = 'Документ щодо передання'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'doc_date desc, doc_number desc'
    _parent_store = True
    _parent_name = 'parent_id'

    @api.model
    def _read_domain_type_ids(self):
        domain = [('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id)]
        return domain

    name = fields.Char(index=True, string="Назва документа", compute='_compute_name', store=True)
    subject = fields.Char(index=True, string="Зміст документа")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    doc_date = fields.Date(index=True, string='Дата документа', required=False)
    doc_number = fields.Char(index=True, string='Номер документа', required=False)
    subject_id = fields.Many2one('asset.blocked.subject', string="Адресат", index=True)
    parent_id = fields.Many2one('asset.blocked.document', string="Головний документ", ondelete='restrict', index=True)
    child_ids = fields.One2many('asset.blocked.document', 'parent_id', string="Похідні документи", index=True)  # ondelete='restrict',
    parent_path = fields.Char()  # index=True    
    category_type_id = fields.Many2one(
        comodel_name = 'dgf.base.type',
        string = 'Категорія документа',
        domain = _read_domain_type_ids,
        required=False)  # required=True after initial import    
    # category_id = fields.Selection(
    #     [("transport", "Мобілізація ТЗ"), ("freeuse", "Безоплатне користування"), ("requisition", "Відчуження"), ("claims", "Право на відшкодування")],
    #     string="Категорія документа",
    #     required=True,
    #     copy=False,
    #     # default="transport",
    # )
    description = fields.Text(string='Опис')
    notes = fields.Text(string='Примітки')
    document_file = fields.Binary(string="Образ документа", attachment=True)  # attachment=False
    file_name = fields.Char("І'мя файлу")    
    state = fields.Selection(
        [("draft", "Отримано"), ("approved", "Опрацьовано")],
        string="Стан документа",
        required=True,
        copy=False,
        default="draft",
    )

    # # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         rec_name = self._compose_name()
    #         result.append((record.id, rec_name))
    #     return result

    @api.onchange('state')
    def _onchange_state(self):
        for record in self:
            if all([record.state == 'approved', any([record.doc_date is False, record.doc_number is False])]):
                msg = 'Для зміни стану документа на "Затверджено" необхідно вказати його дату та номер.'
                raise UserError(msg)

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                # continue
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    @api.depends('doc_number', 'doc_date')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        date_formatted = record.doc_date.strftime('%d.%m.%Y') if record.doc_date is not False else False
        result = "Лист №{0} від {1}".format(record.doc_number, date_formatted)
        return result
