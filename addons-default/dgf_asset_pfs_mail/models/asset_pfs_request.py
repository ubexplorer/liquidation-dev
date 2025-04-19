# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta
import base64

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class AssetPfsRequest(models.Model):
    _name = 'asset.pfs.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _description = 'Пропозиція про продаж майна'
    is_base_stage = True
    is_base_type = True
    _order = "code desc"
    _rec_name = "code"
    _check_company_auto = True

    # def _creation_subtype(self):
    #     return self.env.ref('maintenance.mt_req_created')

    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'stage_id' in init_values:
    #         return self.env.ref('maintenance.mt_req_status')
    #     return super(AssetNfsRequest, self)._track_subtype(init_values)

    # def _get_default_team_id(self):
    #     MT = self.env['maintenance.team']
    #     team = MT.search([('company_id', '=', self.env.company.id)], limit=1)
    #     if not team:
    #         team = MT.search([], limit=1)
    #     return team.id

    name = fields.Char(string='Найменування', compute='_compute_name', store=True, index=True)
    subject = fields.Char(string='Тема повідомлення', index=True)
    description = fields.Html(string='Тіло повідомлення')
    company_id = fields.Many2one('res.company', string='Банк', required=False)  # compute='_compute_company_id'
    email_from = fields.Char(string='Відправник', readonly=True)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence    
    request_date = fields.Date('Дата отримання', default=fields.Date.today())
    close_date = fields.Date('Дата виконання')
    type_id = fields.Many2one(string='Тип заявки', required=False)
    type_code = fields.Char(string='Код типу заявки', related="type_id.code", readonly=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related="stage_id.code", readonly=True)
    user_id = fields.Many2one('res.users', string='Виконавець', default=lambda self: self.env.user, tracking=True)
    active = fields.Boolean(string='Активно', default=True)

    # done = fields.Boolean(string='Виконано', related='stage_id.done')
    # request_number = fields.Char('Номер заявки', tracking=False)
    # asset_nfs_list_id = fields.Many2one('asset.nfs.list', string="Перелік майна", ondelete='restrict', required=True, index=True, check_company=True)
    # document_id = fields.Many2one('dgf.document', string="Рішення про затвердження", ondelete='restrict', index=True)  # domain="[('partner_ids', 'in', company_id.partner_id)]"    
    # off_memo_1_attrs = fields.Char(string='Реквізити відповіді бек-офісу')
    # off_memo_2_attrs = fields.Char(string='Реквізити відповіді стягнення')
    # asset_nfs_ids = fields.One2many(string="Майно у заявці на включення", comodel_name='asset.nfs.list.item', inverse_name='request_id', index=True)
    # maintenance_team_id = fields.Many2one('maintenance.team', string='Team', required=True, default=_get_default_team_id, check_company=True)
    # owner_user_id = fields.Many2one('res.users', string='Created by User', default=lambda s: s.env.uid)    
    # item_count = fields.Integer(string="Майна всього", compute='_compute_item_count', store=True)
    # item_count_active = fields.Integer(string="Майна включено", compute='_compute_item_count', store=True)
    # request_item_count = fields.Integer(string="Майна в запиті", compute='_compute_request_item_count', store=True)
    # template_subject = fields.Text('Тема документа', compute='_compute_template_data', store=True)
    # template_description = fields.Text('Текст документа', compute='_compute_template_data', store=True)
    # template_suffix = fields.Text('Суфікс документа', compute='_compute_template_data', store=True)

    
    @api.depends('type_id')
    def _compute_company_id(self):
        for record in self:
            pass
            # record.company_id = self._compose_name(record) 
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        domain = domain + [('res_model_id', '=', self.env.ref('dgf_asset_pfs_mail.model_asset_pfs_request').id)]
        stage_ids = stages._search(domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('company_id', 'code', 'type_id')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        result = "Пропозиція №{0} - {1}".format(record.code, record.company_id.name)
        return result

    # ----------
    # CRUD overrides
    # ----------
    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_pfs_mail.asset_pfs_request_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------
    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        # aliases = self.mapped('project_id.alias_name')
        # return [x for x in email_list if x.split('@')[0] not in aliases]

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        email_from = msg.get('from')
        normalized_email = tools.email_normalize(email_from)
        # sender_company_id = self.env['hr.employee'].search([('work_email', '=', normalized_email)]).company_id.id or False
        subject = msg.get('subject') or False
        description = msg.get('body') or False
        sender_company_id = self.env['hr.employee'].search([('work_email', 'ilike', normalized_email)], limit=1).company_id.id or False
        if custom_values is None:
            custom_values = {}
        defaults = {            
            'email_from': email_from,
            'subject': subject,
            'description': description,
            # 'email_from': email_from,            
            'company_id': sender_company_id
        }
        defaults.update(custom_values)
        request = super(AssetPfsRequest, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        return request


    # def message_update(self, msg, update_vals=None):
    #     """ Override to update the task according to the email. """
    #     email_list = self.email_split(msg)
    #     partner_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=self, force_create=False) if p]
    #     self.message_subscribe(partner_ids)
    #     return super(Task, self).message_update(msg, update_vals=update_vals)

    # def _message_get_suggested_recipients(self):
    #     recipients = super(Task, self)._message_get_suggested_recipients()
    #     for task in self:
    #         if task.partner_id:
    #             reason = _('Customer Email') if task.partner_id.email else _('Customer')
    #             task._message_add_suggested_recipient(recipients, partner=task.partner_id, reason=reason)
    #         elif task.email_from:
    #             task._message_add_suggested_recipient(recipients, email=task.email_from, reason=_('Customer Email'))
    #     return recipients



    # ----------
    # Not used
    # ----------
    # @api.onchange('stage_id')
    # def _onchange_state(self):
    #     for record in self:
    #         self._change_state(record.stage_id)

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         asset_nfs_list_id = self.env['asset.nfs.list'].search([('company_id', '=', self.company_id.id)], limit=1)
    #         if asset_nfs_list_id.id:
    #             self.asset_nfs_list_id = asset_nfs_list_id
    #         else:
    #             msg = "Перелік майна {company_name}, що не підлягає продажу вісутній. Його необхідно створити".format(company_name=self.company_id.name)
    #             raise UserError(msg)

    # @api.depends('type_id', 'company_id', 'asset_nfs_list_id')
    # def _compute_template_data(self):
    #     for item in self:
    #         if all([item.type_id, item.type_id.description, item.company_id, item.asset_nfs_list_id]):            
    #             # TODO: handle None/False values
    #             # change to mail_template?
    #             if item.type_code == 'approve':
    #                 list_document_date = False
    #                 list_document_no = False
    #             else:
    #                 if not item.asset_nfs_list_id.document_id:
    #                     msg = "В картці 'Перелік майна' необхідно вказати реквізити рішення про його затвердження".format(company_name=self.company_id.name)
    #                     raise UserError(msg)
    #                 list_document_date = item.asset_nfs_list_id.document_id.doc_date.strftime('%d.%m.%Y')
    #                 list_document_no = item.asset_nfs_list_id.document_id.doc_number

    #             template = item.type_id.description.split('|')
    #             company_name = item.company_id.name
    #             item.template_subject = template[0].format(company_name=company_name)
    #             item.template_description = template[1].format(company_name=company_name, list_document_date=list_document_date, list_document_no=list_document_no)
    #             item.template_suffix = template[2].format(company_name=company_name)

    # @api.depends('asset_nfs_ids', 'asset_nfs_exclude_ids')
    # def _compute_request_item_count(self):
    #     for item in self:
    #         if item.type_code == 'exclude':
    #             item.request_item_count = len(item.asset_nfs_exclude_ids)
    #         else:
    #             item.request_item_count = len(item.asset_nfs_ids)

    # def set_request_to_item(self):
    #     self.ensure_one()
    #     self.asset_nfs_list_id.asset_nfs_ids.sudo().write({'request_id': self.id})

    # def inprogress_request(self):
    #     stage_id = self.env['base.stage'].search([('code', '=', 'inprogress')], limit=1)
    #     self._change_state(stage_id)

    # def approve_request(self):
    #     stage_id = self.env['base.stage'].search([('code', '=', 'approved')], limit=1)
    #     self._change_state(stage_id)

    # def _change_state(self, new_stage_id):
    #     for record in self:
    #         if new_stage_id.code == 'approved':
    #             if any([record.document_id.id is False, record.asset_nfs_list_id.id is False]):
    #                 msg = """Для зміни стану на "Затверджено" необхідно вказати значення полів: \n"Перелік майна"\n"Рішення про затвердження"."""
    #                 raise UserError(msg)
    #             else:
    #                 record.close_date = fields.Date.context_today(record)
    #                 record.stage_id = new_stage_id.id
    #                 items_model = record.asset_nfs_ids._name
    #                 items_exclude = record.asset_nfs_exclude_ids.mapped('asset_nfs_list_item_id')
    #                 if record.type_id.code == 'exclude':
    #                     items_exclude_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'exclude'), ('res_model_id.model', '=', items_model)], limit=1)
    #                     record_id = record.id if isinstance(record.id, int) else record.ids[0]
    #                     items_exclude.sudo().write({'stage_id': items_exclude_stage_id.id, 'exclude_request_id': record_id})
    #                 elif record.type_id.code in ['include', 'approve']:
    #                     items_include_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'include'), ('res_model_id.model', '=', items_model)], limit=1)
    #                     record.asset_nfs_ids.sudo().write({'stage_id': items_include_stage_id.id})
    #                     # update asset_nfs_list_id.document_id
    #                     if all([record.type_id.code == 'approve', record.asset_nfs_list_id.document_id.id is False]):
    #                         record.asset_nfs_list_id.document_id = record.document_id
    #         elif new_stage_id.code == 'inprogress':
    #             if record.type_id.code == 'exclude':
    #                 asset_nfs_list_item_ids = record.asset_nfs_exclude_ids.mapped('asset_nfs_list_item_id').ids
    #                 items_exclude = record.asset_nfs_exclude_ids.ids
    #                 if len(asset_nfs_list_item_ids) != len(items_exclude):
    #                     msg = """Для продовження необхідно співставити усі позиції майна в розділі "Майно"."""
    #                     raise UserError(msg)
    #                 elif len(items_exclude) == 0:
    #                     msg = """Для продовження необхідно додати майно в розділі "Майно"."""
    #                     raise UserError(msg)
    #                 else:
    #                     record.stage_id = new_stage_id
    #             else:
    #                 if len(record.asset_nfs_ids.ids) == 0:
    #                     msg = """Для продовження необхідно додати майно в розділі "Майно"."""
    #                     raise UserError(msg)
    #                 else:
    #                     record.stage_id = new_stage_id
    #         else:
    #             record.stage_id = new_stage_id
 
