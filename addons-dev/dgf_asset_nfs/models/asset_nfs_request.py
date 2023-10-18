# -*- coding: utf-8 -*-

import ast

from datetime import date, datetime, timedelta
import base64

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class AssetNfsRequest(models.Model):
    _name = 'asset.nfs.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.stage.abstract', 'base.type.abstract']
    _description = 'Запит щодо майна не для продажу'
    is_base_stage = True
    is_base_type = True
    _order = "code desc"
    _check_company_auto = True
    # _list_name_template = "Перелік майна {}, що не підлягає продажу"

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
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    company_id = fields.Many2one('res.company', string='Банк', required=True)
    request_date = fields.Date('Дата запиту', tracking=False)
    request_number = fields.Char('Номер запиту', tracking=False)
    asset_nfs_list_id = fields.Many2one('asset.nfs.list', string="Перелік майна", ondelete='restrict', required=True, index=True, check_company=True)
    document_id = fields.Many2one('dgf.document', string="Рішення про затвердження", ondelete='restrict', index=True)  # domain="[('partner_ids', 'in', company_id.partner_id)]"
    close_date = fields.Date('Фактична дата виконання')

    priority = fields.Selection([('0', 'Дуже низький'), ('1', 'Низький'), ('2', 'Нормальний'), ('3', 'Високий')], string='Пріоритет')
    schedule_date = fields.Datetime('Очікувана дата виконання')  # default=fields.Date.context_today
    duration = fields.Float(string='Тривалість', help="Тривалість у днях.")
    request_type = fields.Selection([('include', 'Включити до переліку'), ('exclude', 'Виключити з переліку')], string='Тип запиту', default="include")
    color = fields.Integer('Color Index')

    description = fields.Text('Опис')
    asset_nfs_ids = fields.One2many(string="Майно у запиті на включення", comodel_name='asset.nfs.list.item', inverse_name='request_id', ondelete='restrict', index=True)
    asset_nfs_exclude_ids = fields.One2many(string="Майно у запиті на виключення", comodel_name='asset.nfs.request.item', inverse_name='request_id', ondelete='restrict', index=True)
    type_id = fields.Many2one(string='Тип запиту', copy=True, required=True)
    type_code = fields.Char(string='Код типу запиту', related="type_id.code", readonly=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related="stage_id.code", readonly=True)    
    active = fields.Boolean(string='Активно', default=True)
    # done = fields.Boolean(string='Виконано', related='stage_id.done')
    user_id = fields.Many2one('res.users', string='Виконавець', default=lambda self: self.env.user, tracking=True)
    # maintenance_team_id = fields.Many2one('maintenance.team', string='Team', required=True, default=_get_default_team_id, check_company=True)
    # owner_user_id = fields.Many2one('res.users', string='Created by User', default=lambda s: s.env.uid)
    # kanban_state = fields.Selection([('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Ready for next stage')],
    #                                 string='Kanban State', required=True, default='normal', tracking=True)
    request_item_count = fields.Integer(string="Asset Count", compute='_compute_request_item_count')
    template_subject = fields.Text('Тема документа', compute='_compute_template_data', store=True)
    template_description = fields.Text('Текст документа', compute='_compute_template_data', store=True)
    template_suffix = fields.Text('Суфікс документа', compute='_compute_template_data', store=True)

    @api.onchange('stage_id')
    def _onchange_state(self):
        for record in self:
            self._change_state(record.stage_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            asset_nfs_list_id = self.env['asset.nfs.list'].search([('company_id', '=', self.company_id.id)], limit=1)
            if asset_nfs_list_id.id:
                self.asset_nfs_list_id = asset_nfs_list_id
            else:
                msg = "Перелік майна {company_name}, що не підлягає продажу вісутній. Його необхідно створити".format(company_name=self.company_id.name)
                raise UserError(msg)

    @api.depends('type_id', 'company_id', 'asset_nfs_list_id')
    def _compute_template_data(self):
        for item in self:
            if item.type_id and item.type_id.description:
                # TODO: handle None/False values
                # change to mail_template?
                template = item.type_id.description.split('|')
                company_name = item.company_id.name
                list_document_date = item.asset_nfs_list_id.document_id.doc_date.strftime('%d.%m.%Y')
                list_document_no = item.asset_nfs_list_id.document_id.doc_number
                item.template_subject = template[0].format(company_name=company_name)
                item.template_description = template[1].format(company_name=company_name, list_document_date=list_document_date, list_document_no=list_document_no)
                item.template_suffix = template[2].format(company_name=company_name)

    @api.depends('asset_nfs_ids')
    def _compute_request_item_count(self):
        for item in self:
            item.request_item_count = len(item.asset_nfs_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        domain = domain + [('res_model_id', '=', self.env.ref('dgf_asset_nfs.model_asset_nfs_request').id)]
        stage_ids = stages._search(domain, order=order, access_rights_uid=SUPERUSER_ID)
        # stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('company_id', 'code', 'type_id')
    def _compute_name(self):
        for record in self:
            record.name = self._compose_name(record)

    @api.model
    def _compose_name(self, record):
        # date_formatted = record.request_date.strftime('%d.%m.%Y') if record.request_date is not False else False
        result = "Запит №{0} - {1}".format(record.code, record.company_id.name)
        return result

    def approve_request(self):
        # self.write({'stage_code': 'approved'})
        stage_id = self.env['base.stage'].search([('code', '=', 'approved')], limit=1)
        self._change_state(stage_id)

    def _change_state(self, new_stage_id):
        for record in self:
            if new_stage_id.code == 'approved':
                if any([record.document_id.id is False, record.asset_nfs_list_id.id is False]):
                    msg = """Для зміни стану на "Затверджено" необхідно вказати значення полів: \n"Перелік майна"\n"Рішення про затвердження"."""
                    raise UserError(msg)
                else:
                    record.close_date = fields.Date.context_today(record)
                    record.stage_id = new_stage_id.id
                    items_model = record.asset_nfs_ids._name
                    items_exclude = record.asset_nfs_exclude_ids.mapped('asset_nfs_list_item_id')
                    if record.type_id.code == 'exclude':
                        items_exclude_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'exclude'), ('res_model_id.model', '=', items_model)], limit=1)
                        items_exclude.sudo().write({'stage_id': items_exclude_stage_id.id, 'exclude_request_id': record.id})
                    elif record.type_id.code in ['include', 'approve']:
                        items_include_stage_id = self.env['base.stage'].search(['&', ('code', '=', 'include'), ('res_model_id.model', '=', items_model)], limit=1)
                        record.asset_nfs_ids.sudo().write({'stage_id': items_include_stage_id.id})
                        # test: update asset_nfs_list_id.document_id
                        if all([record.type_id.code == 'approve', record.asset_nfs_list_id.document_id.id is False]):
                            record.asset_nfs_list_id.document_id = record.document_id
            else:
                record.stage_id = new_stage_id.id

    def request_list_item_action(self):
        # dgf_asset_nfs_list_item_action_base
        return {
            'type': 'ir.actions.act_window',
            'name': 'Майно не для продажу',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': 'asset.nfs.list.item',
            'view_id': False,
            # 'view_id': self.env.ref('dgf_asset_nfs.dgf_asset_nfs_list_item_tree_base').id,
            # 'view_ids': [(5, 0, 0),
            #     (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('dgf_asset_nfs.dgf_asset_nfs_list_item_tree_base').id}),
            #     (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('dgf_asset_nfs.dgf_asset_nfs_list_item_form').id})],
            'domain': [('request_id', '=', self.id)],            
            'context': {
                'default_request_id': self.id,
                'search_default_include': 1,
                'default_asset_nfs_list_id': self.asset_nfs_list_id.id,
                },
        }

    def request_item_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Майно для викючення',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot',
            'res_model': 'asset.nfs.request.item',
            'view_id': False,
            # 'target': 'new',
            'domain': [('request_id', '=', self.id)],
            # 'domain': [('exclude_request_id', '=', self.id)],
            'context': {
                'default_request_id': self.id,
                # 'search_default_include': 1
                # 'default_exclude_request_id': self.id,
                # 'default_asset_nfs_list_id': self.asset_nfs_list_id.id,
                },
        }

    @api.model
    def create(self, vals):
        sequence = self.env.ref('dgf_asset_nfs.asset_nfs_request_sequence')
        if sequence:
            vals['code'] = sequence.next_by_id()
        return super().create(vals)

    def unlink(self):
        if self.user_has_groups('base.group_erp_manager'):
            return super().unlink()
        else:
            msg = """Заборонено видалення записів."""
            raise UserError(msg)

    # py3o - _get_or_create_single_report
    # def button_validate(self):
    #     if any(statement.state != 'posted' or not statement.all_lines_reconciled for statement in self):
    #         raise UserError(_('All the account entries lines must be processed in order to validate the statement.'))

    #     for statement in self:

    #         # Chatter.
    #         statement.message_post(body=_('Statement %s confirmed.', statement.name))

    #         # Bank statement report.
    #         if statement.journal_id.type == 'bank':
    #             content, content_type = self.env.ref('account.action_report_account_statement')._render(statement.id)
    #             self.env['ir.attachment'].create({
    #                 'name': statement.name and _("Bank Statement %s.pdf", statement.name) or _("Bank Statement.pdf"),
    #                 'type': 'binary',
    #                 'datas': base64.encodebytes(content),
    #                 'res_model': statement._name,
    #                 'res_id': statement.id
    #             })

    #     self._check_balance_end_real_same_as_computed()
    #     self.write({'state': 'confirm', 'date_done': fields.Datetime.now()})


    # test
    # def action_get_attachment(self):
    #     """ This method is used to generate attachment for pdf report"""
    #     pdf = self.env.ref('module_name.report_id')._render_qweb_pdf(self.ids)
    #     b64_pdf = base64.b64encode(pdf[0])
    #     # save pdf as attachment
    #     name = "My Attachment"
    #     return self.env['ir.attachment'].create({
    #         'name': name,
    #         'type': 'binary',
    #         'datas': b64_pdf,
    #         'store_fname': name,
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/x-pdf'
    #     })

    # def generate_report_file(self, id):
    #     pdf = self.env.ref('mymodule.action_report_labtest').render_qweb_pdf(id)[0]
    #     pdf = base64.b64encode(pdf)
    #     return pdf

    # def action_test(self):
    #     report_binary = self.generate_report_file(LabObj.id)
    #     attachmentObj = self.env['ir.attachment'].create({
    #         'name': attachment_name,
    #         'type': 'binary',
    #         'datas': report_binary,
    #         'datas_fname': attachment_name + '.pdf',
    #         'store_fname': attachment_name,
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/x-pdf'
    #     })

    # sync asset_nfs_exclude_ids with asset_nfs_ids
    # def map_exclude_ids(self):
    #     for record in self:
    #         if record.type_id.code == 'exclude':
    #             if record.asset_nfs_ids:  # len(record.asset_nfs_ids) == len(items_exclude)
    #                 msg = "Активи в переліку вже ідентифіковано."
    #                 raise UserError(msg)
    #             else:
    #                 items_exclude = record.asset_nfs_exclude_ids.mapped('asset_nfs_list_item_id')
    #                 if items_exclude:
    #                     record.asset_nfs_ids = [(6, 0, items_exclude.ids)]
    #                 else:
    #                     msg = "Активи для виключення не імпоротовано."
    #                     raise UserError(msg)

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

    # def archive_equipment_request(self):
    #     self.write({'archive': True})

    # def reset_equipment_request(self):
    #     """ Reinsert the maintenance request into the maintenance pipe in the first stage"""
    #     first_stage_obj = self.env['maintenance.stage'].search([], order="sequence asc", limit=1)
    #     # self.write({'active': True, 'stage_id': first_stage_obj.id})
    #     self.write({'archive': False, 'stage_id': first_stage_obj.id})

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id and self.maintenance_team_id:
    #         if self.maintenance_team_id.company_id and not self.maintenance_team_id.company_id.id == self.company_id.id:
    #             self.maintenance_team_id = False

    #     @api.depends('equipment_ids')
    #     def _compute_equipment(self):
    #         for team in self:
    #             team.equipment_count = len(team.equipment_ids)
