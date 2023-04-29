# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, SUPERUSER_ID


class DgfAsset(models.Model):
    _name = 'dgf.asset'
    _description = 'Актив'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'
    # _order = 'doc_date desc'
    _check_company_auto = True

    ###
    # def _get_default_stage_id(self):
    #     """ Gives default stage_id """
    #     project_id = self.env.context.get('default_project_id')
    #     if not project_id:
    #         return False
    #     return self.stage_find(project_id, [('fold', '=', False), ('is_closed', '=', False)])

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     search_domain = [('id', 'in', stages.ids)]
    #     if 'default_project_id' in self.env.context:
    #         search_domain = [
    #             '|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

    #     stage_ids = stages._search(
    #         search_domain, order=order, access_rights_uid=SUPERUSER_ID)
    #     return stages.browse(stage_ids)
    ####

    name = fields.Char(index=True, string="Найменування")
    address = fields.Char(index=True, string="Адреса")
    odb_id = fields.Integer(index=True, string="ID активу в ОДБ")
    eois_id = fields.Integer(index=True, string="ID активу в ЄОІС")
    category_id = fields.Many2one(
        comodel_name='stat.classifier.item', string='Категорія',
        ondelete='restrict',
        context={},
        domain=[('classifier_code', '=', 'asset_category')],)
    type_id = fields.Many2one(
        comodel_name='stat.classifier.item', string='Тип активу',
        ondelete='restrict',
        context={},
        domain=[('classifier_code', '=', 'asset_type'), ('is_group', '=', False)],)
    group_id = fields.Many2one(string='Група активу', related='type_id.parent_id', readonly=True)
    # group_id = fields.Many2one(
    #     comodel_name='stat.classifier.item', string='Група',
    #     ondelete='restrict',
    #     context={},
    #     domain=[('classifier_code', '=', 'asset_type'), ('is_group', '=', True)],)

    bal_account = fields.Char(index=True, string="Балансовий рахунок")
    sku = fields.Char(index=True, string="Номер активу",
                      help="Номер активу (інвентарний, номер договору тощо)")
    dateonbalance = fields.Date(index=True, string='Дата набуття',
                                help="Дата активу (дата оприбуткування на баланс, дата договору тощо)")
    currency_id = fields.Many2one(
        'res.currency', required=True, string='Валюта', default=lambda self: self.env.ref('base.UAH'))
    book_value = fields.Float(string='Балансова вартість', digits=(15, 2))
    # book_value = fields.Monetary(string='Балансова вартість', currency_field='currency_id', store=True, compute='_compute_book_value')
    apprisal_value = fields.Float(string='Оціночна вартість', digits=(15, 2))
    company_partner_id = fields.Many2one(
        'dgf.company.partner', string='Контрагент',
        ondelete='restrict',
        context={},
        #  company_dependent = True
        # domain=[('company_id', '=', lambda self: self.env.company)]
        domain=[])
    company_partner_vat = fields.Char(string='Код контрагента', related='company_partner_id.vat', readonly=True)

    active = fields.Boolean(default=True, string='Активно',
                            help="Чи є запис активним чи архівованим.")
    state = fields.Selection(
        [("run", "На учете"), ("forsale", "В НбА для продажи"),
         ("sold", "Продано"), ("off", "Списано")],
        string="Стан картки",
        required=True,
        copy=False,
        default="run",
    )

    # realty
    reg_num = fields.Char(string="Реєстраційний номер")
    living_area = fields.Float('Житлова площа', digits=(10, 4))
    total_area = fields.Float('Загальна площа', digits=(10, 4))
    register_type_id = fields.Many2one(
        comodel_name='stat.classifier.item', string='Тип реєстру',
        ondelete='restrict',
        context={},
        domain=[('classifier_code', '=', 'register_type')],)
    cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")

    # loans
    currentdebt = fields.Float('Тіло', digits=(15, 2))
    currentinterest = fields.Float('Проценти', digits=(15, 2))
    currentcomissision = fields.Float('Комісії', digits=(15, 2))
    writeoffdebt = fields.Float('Списаний борг', digits=(15, 2))
    totaldebt = fields.Float('Загальний борг', digits=(15, 2), compute='_compute_totaldebt', store=True, readonly=True)
    mortgage_description = fields.Text(string='Опис забезпечення')

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     for record in self:
    #         return {domain:{[('company_id', '=', record.company_id)]}}

    @api.depends('currentdebt', 'currentinterest', 'currentcomissision', 'writeoffdebt')
    def _compute_totaldebt(self):
        for item in self:
            item.totaldebt = item.currentdebt + item.currentinterest + item.currentcomissision + item.writeoffdebt

    @api.depends('totaldebt')
    def _compute_book_value(self):
        for item in self:
            item.book_value = item.totaldebt

    @api.depends('sku', 'dateonbalance')
    def _compute_name(self):
        for item in self:
            item.name = 'КД №{0} від {1}'.format(item.sku, item.dateonbalance)

    ###
    # stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
    #                            store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
    #                            default=_get_default_stage_id, group_expand='_read_group_stage_ids',
    #                            # domain="[('project_ids', '=', project_id)]",
    #                            copy=False)

    # @api.depends('stage_id')
    # def _compute_stage_id(self):
    #     for task in self:
    #         if task.project_id:
    #             if task.project_id not in task.stage_id.project_ids:
    #                 task.stage_id = task.stage_find(task.project_id.id, [
    #                     ('fold', '=', False), ('is_closed', '=', False)])
    #         else:
    #             task.stage_id = False

    ###

    description = fields.Text('Опис активу')
    notes = fields.Text('Примітки')
    company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)

    # # dynamic field label
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(DgfAsset, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(result['arch'])
    #         field = doc.xpath("//field[@name='sku']")
    #         if field:
    #             print(self.type_id)
    #             field[0].set("string", "Динамічний Номер активу")
    #             # sale_reference[0].addnext(etree.Element('label', {'string': 'Sale Reference Number'}))
    #             result['arch'] = etree.tostring(doc, encoding='unicode')
    #     return result

    # doc_date = fields.Date(index=True, string='Дата документа')
    # doc_number = fields.Char(index=True, string='Номер документа')
    # department_id = fields.Many2one('hr.department', string='Орган, що видав', index=True, domain="[('is_body','=',True)]")
    # parent_document_id = fields.Many2one('dgf.document', string="Пов'язаний документ", readonly="True", index=True)
    # document_type_id = fields.Many2one('dgf.document.type', string='Тип документа', index=True)
    # category_id = fields.Many2one('dgf.document.category', string='Категорія', index=True)
    # description = fields.Text(string='Опис')
    # notes = fields.Text(string='Примітки')
    # document_file = fields.Binary(string="Образ документа", attachment=True)  # attachment=False
    # file_name = fields.Char("І'мя файлу")
    # # partner_id = fields.Many2one('res.partner', required=True)
    # partner_ids = fields.Many2many('res.partner', 'dgf_doc_res_partner_rel', 'doc_id', 'partner_id', string='Банки', required=True, domain="[('is_company','=',True)]")

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         rec_name = "{0} №{1} від {2}".format(record.document_type_id.name, record.doc_number, record.doc_date)
    #         result.append((record.id, rec_name))
    #     return result

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

    # def action_create_from_parent(self):
    #     print("self.id: {0}".format(self.id))
    #     banks = self.partner_ids.ids
    #     print(banks)
    #     return {
    #         'name': 'Документи',
    #         'view_type': 'form',
    #         'res_model': 'dgf.document',
    #         'view_id': False,
    #         'view_mode': 'form',
    #         # 'target': 'new',
    #         'context': {
    #             'default_parent_document_id': self.id,
    #             'default_category_id': self.category_id.id,
    #             'default_document_type_id': self.document_type_id.id,   # serch document_type_id
    #             # 'default_department_id': self.department_id.id,  # serch department_id
    #             'default_partner_ids': banks,
    #             'default_name': self.name},
    #         'type': 'ir.actions.act_window'
    #     }
