# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta
import base64

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class AssetBlockedRequest(models.Model):
    _name = 'asset.blocked.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _description = 'Заявка щодо майна блокованого'
    is_base_stage = True
    is_base_type = True
    _order = "code desc"
    _rec_name = "code"
    _parent_store = True
    _check_company_auto = False

    name = fields.Char(string='Найменування', compute='_compute_name', store=True, index=True)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    company_id = fields.Many2one('res.company', string='Банк') #  , required=True
    subject_id = fields.Many2one('asset.blocked.subject', string="Ініціатор", index=True)
    # blocked_document_ids = fields.One2many('asset.blocked.document', 'parent_id', string="Похідні документи", index=True)  # ondelete='restrict',
    blocked_document_ids = fields.Many2many('asset.blocked.document', string='Документи щодо передання', domain="[('subject_id', '=', subject_id), ('state', '=', 'draft')]")
    request_date = fields.Date('Дата заявки', tracking=False)
    request_number = fields.Char('Номер заявки', tracking=False)
    asset_blocked_list_id = fields.Many2one('asset.blocked.list', string="Перелік майна", ondelete='restrict', index=True, check_company=False) # required=True, 
    document_id = fields.Many2one('dgf.document.blocked', string="Рішення про затвердження", ondelete='restrict', index=True)  # domain="[('partner_ids', 'in', company_id.partner_id)]"
    document_date = fields.Date(string='Дата затвердження', related="document_id.doc_date", readonly=True)
    close_date = fields.Date('Фактична дата виконання')
    aquirer_id = fields.Many2one('asset.blocked.subject', string="Отримувач", index=True)
    transfer_date = fields.Date(string='Дата передання')
    description = fields.Text('Опис')
    memo = fields.Char(string='Примітки')
    document_letters = fields.Char(string='Реквізити звернення')
    document_reasons = fields.Char(string='Реквізити документів-підстав')
    document_transfers = fields.Char(string='Реквізити документів про передання')

    asset_blocked_ids = fields.One2many(string="Майно у заявці на включення", comodel_name='asset.blocked.list.item', inverse_name='request_id', index=True)
    asset_blocked_exclude_ids = fields.One2many(string="Майно у заявці на виключення", comodel_name='asset.blocked.request.item', inverse_name='request_id', index=True)
    type_id = fields.Many2one(string='Тип заявки', required=False)  # required=True after initial import
    type_code = fields.Char(string='Код типу заявки', related="type_id.code", readonly=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related="stage_id.code", readonly=True)
    active = fields.Boolean(string='Активно', default=True)
    server_in_request = fields.Boolean(string='В заявці є сервери')  # add compute='_compute_servers',
    is_closed = fields.Boolean(string='Виконано', related='stage_id.is_closed')
    user_id = fields.Many2one('res.users', string='Виконавець', default=lambda self: self.env.user, tracking=True)

    request_item_count = fields.Integer(string="Майна до включення", compute='_compute_request_item_count', store=False, readonly=True)
    request_item_exclude_count = fields.Integer(string="Майна до виключення", compute='_compute_request_item_count', store=False, readonly=True)
    request_total_book_value_uah = fields.Float(string='Загальна БВ (включення)', compute='_compute_request_totals', store=True, digits=(15, 2), readonly=True)
    request_total_apprisal_value = fields.Float(string='Загальна ОВ (включення)', compute='_compute_request_totals', store=True, digits=(15, 2), readonly=True)
    request_total_transfer_value = fields.Float(string='Загальна вартість передання, UAH', compute='_compute_request_totals', store=True, digits=(15, 2), readonly=True)
    exclude_total_book_value_uah = fields.Float(string='Загальна БВ (виключення)', compute='_compute_request_totals', store=True, digits=(15, 2), readonly=True)
    exclude_total_apprisal_value = fields.Float(string='Загальна ОВ (виключення)', compute='_compute_request_totals', store=True, digits=(15, 2), readonly=True)

    template_subject = fields.Text('Тема документа', compute='_compute_template_data', store=True)
    # template_description = fields.Text('Текст документа', compute='_compute_template_data', store=True)
    template_suffix = fields.Text('Назва додатку', compute='_compute_template_data', store=True)
    # body_html = fields.Html('Текст шаблону', sanitize=False)
    agreement_ids = fields.One2many(string="Пов'язані договори", comodel_name='asset.blocked.agreement', inverse_name='request_id', index=True)

    parent_id = fields.Many2one('asset.blocked.request', string='Головна заявка', ondelete='restrict', index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('asset.blocked.request', 'parent_id', string='Дочірні заявки')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            asset_blocked_list_id = self.env['asset.blocked.list'].search([('company_id', '=', self.company_id.id)], limit=1)
            if asset_blocked_list_id.id:
                self.asset_blocked_list_id = asset_blocked_list_id
            else:
                msg = "Перелік майна {company_name} вісутній. Його необхідно створити".format(company_name=self.company_id.name)
                raise UserError(msg)

    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        for record in self:
            record.aquirer_id = record.subject_id

    # for report
    @api.depends('type_id', 'company_id', 'aquirer_id')
    def _compute_template_data(self):
        for item in self:
            if item.type_code in ['exclude']:
                company_name = item.company_id.name
                template_data = item.type_id.description.format(company_name=company_name)
                template = template_data.split('\n')
                item.template_subject = template[0]
                item.template_suffix = template[1]
            else:
                if all([item.type_id, item.type_id.description, item.company_id, item.aquirer_id]):
                    company_name = item.company_id.name
                    aquirer_name = self.aquirer_id.fullname
                    template_data = item.type_id.description.format(company_name=company_name, aquirer_name=aquirer_name)
                    template = template_data.split('\n')
                    item.template_subject = template[0]
                    item.template_suffix = template[1]

    # for report; not in use
    @api.depends('type_id', 'company_id', 'aquirer_id')
    def py3o_report_data(self):
        self.ensure_one()
        res = {}
        company_name = self.company_id.name
        aquirer_name = self.aquirer_id.fullname
        template = self.type_id.description.split('\n')
        doc_subject = template[0].format(company_name=company_name)
        doc_list_name = template[1].format(company_name=company_name, aquirer_name=aquirer_name)

        res['doc_subject'] = doc_subject
        res['doc_list_name'] = doc_list_name
        return res

    # for report
    def rvd_lines_text(self):
        self.ensure_one()
        res = []
        rvd_template_data = self._compute_rvd_template_fields()
        if rvd_template_data:
            lines = rvd_template_data.split('\n')
            line_index = 1
            for line in lines:
                res.append({'line_text': line})
        return res

    def _compute_rvd_template_fields(self):
        for record in self:
            if record.type_id.rvd_template_id and record.id:
                document_text = record.type_id.rvd_template_id._render_field('body_html', [record.id])[record.id]
            else:
                document_text = record.type_id.rvd_template_id.body_html
            return document_text

    def dz_lines_text(self):
        self.ensure_one()
        res = []
        dz_template_data = self._compute_dz_template_fields()
        if dz_template_data:
            lines = dz_template_data.split('\n')
            line_index = 1
            for line in lines:
                res.append({'line_text': line})
        return res

    def _compute_dz_template_fields(self):
        for record in self:
            if record.type_id.dz_template_id and record.id:
                document_text = record.type_id.dz_template_id._render_field('body_html', [record.id])[record.id]
            else:
                document_text = record.type_id.dz_template_id.body_html
            return document_text

    @api.depends('asset_blocked_ids', 'asset_blocked_exclude_ids')
    def _compute_request_item_count(self):
        for item in self:
            item.request_item_count = len(item.asset_blocked_ids)
            item.request_item_exclude_count = len(item.asset_blocked_exclude_ids)

    @api.depends('asset_blocked_ids', 'asset_blocked_exclude_ids')
    def _compute_request_totals(self):
        for record in self:
            record.request_total_book_value_uah = sum(item.book_value_uah for item in record.asset_blocked_ids)
            record.request_total_apprisal_value = sum(item.apprisal_value for item in record.asset_blocked_ids)
            record.exclude_total_book_value_uah = sum(item.book_value_uah for item in record.asset_blocked_exclude_ids)
            record.exclude_total_apprisal_value = sum(item.apprisal_value for item in record.asset_blocked_exclude_ids)                

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        domain = domain + [('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id)]
        stage_ids = stages._search(domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('document_id', 'code', 'type_id')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        result = "[{0}] {1}".format(record.code, record.document_id.name)
        return result

    # def set_request_to_item(self):
    #     self.ensure_one()
    #     self.asset_blocked_list_id.asset_blocked_ids.sudo().write({'request_id': self.id})

    def set_dz_to_agreement(self):
        self.ensure_one()
        if len(self.asset_blocked_ids.ids) > 1:
            msg = """Кількість ДЗ, в яку перекласифіковується майно, не має перевищувати 1."""
            raise UserError(msg)
        else:
            dz_included_id =  self.asset_blocked_ids.ids[0]
            # set included item_id to related agreement
            self.parent_id.agreement_ids.sudo().write({'asset_blocked_dz_id': dz_included_id})
            # set included item_id as parent_id to related excluded item_ids
            items_exclude = self.asset_blocked_exclude_ids.mapped('asset_blocked_list_item_id')
            items_exclude.sudo().write({'parent_id': dz_included_id})

    def set_exclude_ids(self):
        self.ensure_one()
        # "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
        # use the same method to set child items to 'asset.blocked.list.item'
        vals_to_insert = []
        for item in self.parent_id.asset_blocked_ids:
            val = {
                'request_id': self.id,
                'code_import': item.code,
                'asset_blocked_list_item_id': item.id,
            }
            vals_to_insert.append(val)
        exclude_items = self.env['asset.blocked.request.item']
        exclude_items.create(vals_to_insert)

    def inprogress_request(self):
        stage_id = self.env['base.stage'].search([
            '&',
            ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
            ('code', '=', 'inprogress'),
            ], limit=1)
        self._change_state(stage_id)
        if self.type_code == 'claims':
            self.set_dz_to_agreement()

    def approve_request(self):
        stage_id = self.env['base.stage'].search([
            '&',
            ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
            ('code', '=', 'approved')], limit=1)
        self._change_state(stage_id)

    def mark_delivered(self):
        stage_delivered = self.env['base.stage'].search([
            '&',
            ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
            ('code', '=', 'delivered')], limit=1)
        stage_transferred = self.env['base.stage'].search([
            '&',
            ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
            ('code', '=', 'transferred')], limit=1)
        stage_id = stage_transferred if self.type_code == 'claims' else stage_delivered
        self._change_state(stage_id)

    def _change_state(self, new_stage_id):
        # Переробити логіку
        for record in self:
            if new_stage_id.code == 'approved':
                if any([record.document_id.id is False]):  # , record.asset_blocked_list_id.id is False
                    msg = """Для зміни стану на "Затверджено" необхідно вказати значення полів: \n"Рішення про затвердження"."""
                    raise UserError(msg)
                else:
                    record.close_date = fields.Date.context_today(record)
                    record.stage_id = new_stage_id.id
                    items_model = record.asset_blocked_ids._name
                    items_exclude = record.asset_blocked_exclude_ids.mapped('asset_blocked_list_item_id')

                    items_include_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'include'), ('res_model_id.model', '=', items_model)], limit=1)
                    items_exclude_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'exclude'), ('res_model_id.model', '=', items_model)], limit=1)
                    items_requisition_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'terminated'), ('res_model_id.model', '=', items_model)], limit=1)
                    record_id = record.id if isinstance(record.id, int) else record.ids[0]                    

                    # change logic
                    if record.type_id.code in ['transport', 'freeuse', 'requisition', 'free']:
                        record.asset_blocked_ids.sudo().write({'stage_id': items_include_stage_id.id})
                    elif record.type_id.code == 'exclude':
                        items_exclude.sudo().write({'stage_id': items_exclude_stage_id.id, 'exclude_request_id': record_id})
                    # elif record.type_id.code in ['include', 'approve']:
                    elif record.type_id.code == 'claims':
                        record.asset_blocked_ids.sudo().write({'stage_id': items_include_stage_id.id})
                        items_exclude.sudo().write({'stage_id': items_requisition_stage_id.id, 'exclude_request_id': record_id})
                    else:
                        record.asset_blocked_ids.sudo().write({'stage_id': items_include_stage_id.id})
                    # update asset_blocked_list_id.document_id для МНП: затвердження переліку
                    if all([record.type_id.code == 'approve', record.asset_blocked_list_id.document_id.id is False]):
                        record.asset_blocked_list_id.document_id = record.document_id

            elif new_stage_id.code == 'inprogress':
                if record.type_id.code == 'exclude':
                    asset_blocked_list_item_ids = record.asset_blocked_exclude_ids.mapped('asset_blocked_list_item_id').ids
                    items_exclude = record.asset_blocked_exclude_ids.ids
                    if len(asset_blocked_list_item_ids) != len(items_exclude):
                        msg = """Для продовження необхідно співставити усі позиції майна в розділі "До виключення"."""
                        raise UserError(msg)
                    elif len(items_exclude) == 0:
                        msg = """Для продовження необхідно додати майно в розділі "До виключення"."""
                        raise UserError(msg)
                    else:
                        record.stage_id = new_stage_id
                elif record.type_id.code == 'claims':
                    if any([len(record.asset_blocked_ids.ids) == 0, len(record.asset_blocked_exclude_ids.ids) == 0]):
                        msg = """Для продовження необхідно додати майно в усі розділи:\n- "До включення";\n- "До виключення"."""
                        raise UserError(msg)
                    else:
                        record.stage_id = new_stage_id
                else:
                    if len(record.asset_blocked_ids.ids) == 0:
                        msg = """Для продовження необхідно додати майно в розділі "До включення"."""
                        raise UserError(msg)
                    else:
                        record.stage_id = new_stage_id
            else:
                record.stage_id = new_stage_id

    def request_list_item_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Майно блоковане',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': 'asset.blocked.list.item',
            'view_id': False,
            # 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_tree_base').id,
            # 'view_ids': [(5, 0, 0),
            #     (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_tree_base').id}),
            #     (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('dgf_asset_blocked.dgf_asset_blocked_list_item_form').id})],
            'domain': [('request_id', '=', self.id)],
            'context': {
                'default_request_id': self.id,
                'default_asset_blocked_list_id': self.asset_blocked_list_id.id,
                'default_company_id': self.asset_blocked_list_id.company_id.id,
            },
        }

    def request_item_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Майно для викючення',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': 'asset.blocked.request.item',
            'target': 'current',
            # 'domain': [('request_id', '=', self.id)],
            # 'domain': [('exclude_request_id', '=', self.id)],
            # 'context': {
            #     'default_request_id': self.id,
            # },
        }

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_blocked.asset_blocked_request_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)


    def action_create_agreement(self):
        self.ensure_one()
        # stage_id = self.env['base.stage'].search([
        #     '&',
        #     ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
        #     ('code', '=', 'transferred')], limit=1)
        # self.stage_id = stage_id
        # # виключити зміну статусу майна на передано, хаявки на виконано -  без договору
        # items_stage_id = self.env['base.stage'].search(['&', ('res_model_id.model', '=', 'asset.blocked.list.item'), ('code', '=', 'transferred')], limit=1)
        # self.asset_blocked_ids.sudo().write({'stage_id': items_stage_id.id})
        return {
            'name': 'Договори',
            'view_type': 'form',
            'res_model': 'asset.blocked.agreement',
            'view_id': False,
            'view_mode': 'form',
            # 'target': 'new',
            'context': {
                'default_request_ids': [self.id],
                'default_request_id': self.id,
                'default_company_id': self.company_id.id,
                'default_subject_id': self.aquirer_id.id,
                'default_asset_blocked_ids': self.asset_blocked_ids.ids,
                'request_id': self.id,},
            'type': 'ir.actions.act_window'
        }
    def action_create_request_rel(self):
        self.ensure_one()
        # stage_id = self.env['base.stage'].search([
        #     '&',
        #     ('res_model_id', '=', self.env.ref('dgf_asset_blocked.model_asset_blocked_request').id),
        #     ('code', '=', 'transferred')], limit=1)
        # self.stage_id = stage_id
        # # виключити зміну статусу майна на передано, заявки на виконано -  без договору
        # items_stage_id = self.env['base.stage'].search(['&', ('res_model_id.model', '=', 'asset.blocked.list.item'), ('code', '=', 'transferred')], limit=1)
        # self.asset_blocked_ids.sudo().write({'stage_id': items_stage_id.id})
        items_type_id = self.env['dgf.base.type'].search(['&', ('res_model_id.model', '=', 'asset.blocked.request'), ('code', '=', 'claims')], limit=1)
        return {
            'name': 'Заявка',
            'view_type': 'form',
            'res_model': 'asset.blocked.request',
            'view_id': False,
            'view_mode': 'form',
            # 'target': 'new',
            'context': {
                'default_type_id': items_type_id.id,
                'default_company_id': self.company_id.id,
                'default_asset_blocked_list_id': self.asset_blocked_list_id.id,
                'default_subject_id': self.subject_id.id,
                'default_parent_id': self.id,
            },
            'type': 'ir.actions.act_window'
        }


    # @api.model
    # def _action_context(self):
    #     """
    #     Allows to use active_id & ref('xmlid') in action context in xml view, reffering this function
    #     """
    #     ref = self.env.ref
    #     active_id = unquote("active_id")

    #     return {
    #         'default_document_type_id': ref('dgf_document.decision').id,
    #         'default_department_id': ref('dgf_document.dep_kkupa').id,
    #         'default_parent_document_id': active_id,
    #     }
