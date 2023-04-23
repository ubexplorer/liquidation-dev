# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import unquote


class DgfDocument(models.Model):
    _name = 'dgf.document'
    _description = 'Внутрішній документ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'doc_date desc, doc_number desc'
    _parent_store = True
    _parent_name = 'parent_document_id'

    name = fields.Char(index=True, string="Назва документа", compute='_compute_name', store=True)
    subject = fields.Char(index=True, string="Зміст документа")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    doc_date = fields.Date(index=True, string='Дата документа', required=False)
    doc_number = fields.Char(index=True, string='Номер документа', required=False)
    department_id = fields.Many2one('hr.department', string='Орган, що видав', index=True, required=True, domain="[('is_body','=',True)]")
    parent_document_id = fields.Many2one('dgf.document', string="Прийнято на підставі", ondelete='restrict', index=True)
    child_ids = fields.One2many('dgf.document', 'parent_document_id', string="Похідні документи", index=True)  # ondelete='restrict',
    parent_path = fields.Char()  # index=True
    can_create_child = fields.Boolean(string='Створювати дочірні рішення', compute='_compute_can_child')
    document_type_id = fields.Many2one('dgf.document.type', string='Тип документа', required=True, index=True)
    category_id = fields.Many2one('dgf.document.category', string='Категорія', index=True)
    description = fields.Text(string='Опис')
    notes = fields.Text(string='Примітки')
    document_private_content = fields.Html(string='Зміст документа')
    document_file = fields.Binary(string="Образ документа", attachment=True)  # attachment=False
    file_name = fields.Char("І'мя файлу")
    partner_ids = fields.Many2many('res.partner', 'dgf_doc_res_partner_rel', 'doc_id', 'partner_id', string='Банки', required=True, domain="[('is_company','=',True)]")
    is_public = fields.Boolean(string="Публічний", default=True, groups='dgf_document.group_documents_private')
    state = fields.Selection(
        [("draft", "Чернетка"), ("approved", "Затверджено")],
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

    @api.depends('document_type_id', 'department_id', 'doc_number', 'doc_date')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.depends('department_id')
    def _compute_can_child(self):
        for record in self:
            record.can_create_child = False if record.department_id.id == self.env.ref('dgf_document.dep_vd').id else True

    @api.model
    def _compose_name(self, record):
        date_formatted = record.doc_date.strftime('%d.%m.%Y') if record.doc_date is not False else False
        result = "{0} [{1}] №{2} від {3}".format(record.document_type_id.name, record.department_id.name, record.doc_number, date_formatted)
        return result

    # def log_company_ids(self):
    #     company_id = self.env.user.company_id.id
    #     company_ids = self.env.user.company_ids
    #     allowed_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))

    #     print("company_id:", company_id)
    #     print("company_ids:", company_ids)
    #     print("allowed_company_ids:", allowed_company_ids)
    #     domain = [('company_ids', 'in', allowed_company_ids)]
    #     print(domain)
    #     return True

    def action_create_from_parent(self):
        # print("self.id: {0}".format(self.id))
        banks = self.partner_ids.ids
        # child_ids = self.child_ids
        # print(child_ids)
        return {
            'name': 'Документи',
            'view_type': 'form',
            'res_model': 'dgf.document',
            'view_id': False,
            'view_mode': 'form',
            # 'target': 'new',
            'context': {
                'default_parent_document_id': self.id,
                'default_category_id': self.category_id.id,
                'default_document_type_id': self.env.ref('dgf_document.decision').id,
                'default_department_id': self.env.ref('dgf_document.dep_vd').id,
                'default_partner_ids': banks,
                'default_subject': self.subject,
                'default_is_public': self.is_public},
            'type': 'ir.actions.act_window'
        }

    @api.model
    def _action_context(self):
        """
        Allows to use active_id & ref('xmlid') in action context in xml view, reffering this function
        """
        ref = self.env.ref
        active_id = unquote("active_id")

        return {
            'default_document_type_id': ref('dgf_document.decision').id,
            'default_department_id': ref('dgf_document.dep_kkupa').id,
            'default_parent_document_id': active_id,
        }
