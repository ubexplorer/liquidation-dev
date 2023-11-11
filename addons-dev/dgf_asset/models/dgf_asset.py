# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


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

    name = fields.Char(string="Найменування", index=True, compute='_compute_name', store=False, readonly=False)
    address = fields.Char(index=True, string="Адреса")
    odb_id = fields.Char(index=True, string="ID активу в ОДБ")
    eois_id = fields.Char(index=True, string="ID активу в ЄОІС")
    category_id = fields.Many2one(
        comodel_name='stat.classifier.item', string='Категорія',
        ondelete='restrict',
        context={},
        domain=[('classifier_code', '=', 'asset_category')],)
    type_id = fields.Many2one(
        comodel_name='dgf.asset.category', string='Тип активу',
        ondelete='restrict',
        context={},
        domain=[('is_group', '=', False)],)
    group_id = fields.Many2one(string='Група активу', related='type_id.parent_id', store=True, readonly=True)
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
        check_company=True,
        domain="[('company_id', '=', company_id)]",)
    partner_id = fields.Many2one(string='Контакт', related='company_partner_id.partner_id', readonly=True)
    phone = fields.Char(string='Контакт', related='company_partner_id.phone', readonly=True)
    mobile = fields.Char(string='Контакт', related='company_partner_id.mobile', readonly=True)
    company_partner_vat = fields.Char(string='Код контрагента', related='company_partner_id.vat', readonly=True)
    company_id = fields.Many2one('res.company', string='Банк', required=True, default=lambda self: self.env.company)
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
    stage_id = fields.Many2one('dgf.asset.stage', string='Статус', store=True, readonly=False, ondelete='restrict',
                               tracking=True, index=True,
                               # default=_get_default_stage_id, compute='_compute_stage_id',
                               # group_expand='_read_group_stage_ids',
                               domain="[]", copy=False)

    # realty
    reg_num = fields.Char(string="Реєстраційний номер")
    living_area = fields.Float('Житлова площа', digits=(10, 4))
    total_area = fields.Float('Загальна площа', digits=(10, 4))
    register_type_id = fields.Many2one(
        comodel_name='dgf.asset.register.type', string='Тип реєстру',
        ondelete='restrict',
        context={},
        domain=[],)
    cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")

    # loans
    currentdebt = fields.Float('Тіло', digits=(15, 2))
    currentinterest = fields.Float('Проценти', digits=(15, 2))
    currentcomissision = fields.Float('Комісії', digits=(15, 2))
    writeoffdebt = fields.Float('Списаний борг', digits=(15, 2))
    totaldebt = fields.Float('Загальний борг', digits=(15, 2), compute='_compute_totaldebt', store=True, readonly=True)
    mortgage_description = fields.Text(string='Опис забезпечення')

    # sales
    datesale1 = fields.Date(index=True, string='Дата раунд 1', help="Дата подання пропозиції про реалізацію (раунд 1)")
    datesale2 = fields.Date(index=True, string='Дата раунд 2', help="Дата подання пропозиції про реалізацію (раунд 2)")
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

    @api.depends('sku', 'group_id')
    def _compute_name(self):
        for item in self:
            item.name = '{0} №{1}'.format(item.group_id.name, item.sku)

    ###
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

    # Override default implementation of name_get(), which uses the _rec_name attribute to find which field holds the data, which is used to generate the display name.
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         rec_name = "{0} №{1} від {2}".format(record.document_type_id.name, record.doc_number, record.doc_date)
    #         result.append((record.id, rec_name))
    #     return result

    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile', 'phone']

    def _sms_get_partner_fields(self):
        """ This method returns the fields to use to find the contact to link
        whensending an SMS. Having partner is not necessary, having only phone
        number fields is possible. However it gives more flexibility to
        notifications management when having partners. """
        fields = []
        if hasattr(self, 'partner_id'):
            fields.append('partner_id')
        if hasattr(self, 'partner_ids'):
            fields.append('partner_ids')
        return fields


    def action_update_invoice_date(self):
        selected_assets = self.ids
        print(len(selected_assets))
        print(selected_assets)
        self.write({'datesale1': fields.Date.today()})

    def action_create_lot(self):
        # selected_assets = self.ids
        active_ids = self.env.context.get('active_ids', [])
        lines = []
        for item in active_ids:
            line = (0, 0, {'asset_id': item})
            lines.append(line)
        # print('Records selected: {}'.format(len(active_ids)))
        return {
            'name': 'Лот',
            'view_type': 'form',
            'res_model': 'dgf.auction.lot',
            'view_id': False,
            'view_mode': 'form',
            # 'target': 'new',
            'context': {
                # 'default_parent_document_id': self.id,
                # 'default_category_id': self.category_id.id,
                # 'default_document_type_id': self.document_type_id.id,   # serch document_type_id
                # 'default_department_id': self.department_id.id,  # serch department_id
                # TODO: define the right way to add o2m values
                # 'default_asset_ids': [(0, 0, {'asset_id': 12283})]
                'default_asset_ids': lines
            },
            'type': 'ir.actions.act_window'
        }


class DgfAssetCategory(models.Model):
    _description = 'Категорії активів'
    _name = 'dgf.asset.category'
    _order = 'sequence'
    _parent_store = True

    sequence = fields.Integer('Послідовність', default=10)
    name = fields.Char(string='Найменування', required=True)
    # full_name = fields.Char(string='Повне найменування', index=True)
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Код', required=False)
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи активів.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.asset.category', string='Батьківська категорія', ondelete='cascade')  # index=True,
    parent_path = fields.Char()  # index=True
    child_ids = fields.One2many('dgf.asset.category', 'parent_id', string='Дочірні категорії')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (
                    category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class DgfAssetRegisterType(models.Model):
    _description = 'Тип реєстру'
    _name = 'dgf.asset.register.type'
    _order = 'sequence'
    _parent_store = True

    sequence = fields.Integer('Послідовність', default=10)
    name = fields.Char(string='Найменування', required=True)
    # full_name = fields.Char(string='Повне найменування', index=True)
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Код', required=False)
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.asset.register.type', string='Батьківська категорія', ondelete='cascade')  # index=True,
    parent_path = fields.Char()  # index=True
    child_ids = fields.One2many('dgf.asset.register.type', 'parent_id', string='Дочірні категорії')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (
                    category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class DgfAssetStage(models.Model):
    _name = 'dgf.asset.stage'
    _description = 'Статус активу'
    _order = 'sequence, id'

    # def _get_default_project_ids(self):
    #     default_project_id = self.env.context.get('default_project_id')
    #     return [default_project_id] if default_project_id else None

    active = fields.Boolean('Active', default=True)
    code = fields.Char(string='Stage Code', required=True)
    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'dgf.asset')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    is_closed = fields.Boolean(
        'Closing Stage', help="Tasks in this stage are considered as closed.")
