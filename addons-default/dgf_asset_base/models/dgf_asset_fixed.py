# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

ADDRESS_FIELDS = ('street', 'np_id', 'district_id', 'state_id', 'country_id', 'zip')

class DgfAsset(models.Model):
    # _inherit = ['format.address.mixin', 'dgf.asset']
    _inherit = ['dgf.asset']

    ## address block move to dgf_asset_address module
    # district_id = fields.Many2one('res.country.district', string='Район')
    # np_id = fields.Many2one('res.country.np', string='Населений пункт')
    # street = fields.Char(string='Вулиця')
    # zip = fields.Char(string='Індекс', change_default=True)
    # complete_address = fields.Char(compute='_compute_complete_address', string='Повна адреса')    
    # geo_latitude = fields.Float(string='Широта', digits=(16, 5))
    # geo_longitude = fields.Float(string='Довгота', digits=(16, 5))
    
    # register block
    register_type_id = fields.Many2one(
        comodel_name='dgf.asset.register.type', string='Тип реєстру',
        ondelete='restrict',
        context={},
        domain=[],)    
    reg_num = fields.Char(string="Реєстраційний номер")
    total_area = fields.Float('Загальна площа', digits=(10, 4))
    is_living = fields.Boolean(default=False, string='Є житловим', help="Чи є приміщення житловим.")
    living_area = fields.Float('Житлова площа', digits=(10, 4))
    cad_num = fields.Char(string="Кадастровий номер", index=True, help="Кадастровий номер земельної ділянки")

    # ТЗ
    vehicle_type = fields.Selection(
        [
            ('car', 'Автомобіль'),
            ('trailer', 'Причіп'),
            ('bike', 'Мотоцикл'),            
            ('bicycle', 'Велосипед'),
            ('hydrocycle', 'Гідроцикл'),
            ('waterbicycle', 'Велосипед водяний'),
            ('boat', 'Човен'),
            ('other', 'Інше'),
        ], string='Тип ТЗ')
    brand = fields.Char('Марка', help='Марка ТЗ')
    model = fields.Char('Модель', help='Модлеь ТЗ')    
    model_year = fields.Char('Рік випуску', help='Рік випуску ТЗ')
    odometer = fields.Float(string='Пробіг (км)', help='Пробіг ТЗ (км)')
    # brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand', related="model_id.brand_id", store=True, readonly=False)
    # model_id = fields.Many2one('fleet.vehicle.model', 'Model', tracking=True, required=True, help='Model of the vehicle')
    # color = fields.Char(help='Color of the vehicle')    
    # odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Last Odometer', help='Odometer measure of the vehicle at the moment of this log')
    # odometer_unit = fields.Selection([
    #     ('kilometers', 'km'),
    #     ('miles', 'mi')
    #     ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)
    # transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission', help='Transmission Used by the vehicle')
    # fuel_type = fields.Selection([
    #     ('gasoline', 'Gasoline'),
    #     ('diesel', 'Diesel'),
    #     ('lpg', 'LPG'),
    #     ('electric', 'Electric'),
    #     ('hybrid', 'Hybrid')
    #     ], 'Fuel Type', help='Fuel Used by the vehicle')
    # vehicle_type = fields.Selection(related='model_id.vehicle_type')

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)

    @api.model
    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return self._address_fields()

    def update_address(self, vals):
        addr_vals = {key: vals[key] for key in self._address_fields() if key in vals}
        if addr_vals:
            return super().write(addr_vals)

    @api.model
    def _get_default_address_format(self):
        # return "%(street)s\n%(np_id)s %(district_id)s %(state_id)s\n%(country_name)s %(zip)s"
        # return "%(street)s %(np_name)s %(district_name)s %(state_name)s %(zip)s %(country_name)s"
        return "{street} {np_name} {district_name} {state_name} {zip} {country_name}"

    @api.model
    def _get_address_format(self):
        # return self.country_id.address_format or self._get_default_address_format()
        return self._get_default_address_format()

    def _display_address(self):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        # TODO:
        address_format = self._get_address_format()
        args = defaultdict(str, {
            # 'country_name': f'{self.country_id.name}, '  or '',
            # 'state_name': f'{self.state_id.name}, ' or '',  # self.state_id.complete_name or '', ADD complete_name to model
            # 'district_name': f'{self.district_id.name}, ' or '',  # self.district_id.complete_name or '', ADD complete_name to model
            # 'np_name': f'{self.np_id.complete_name}, ' or '',

            # # no formatting
            'street': self.street or '',
            'np_name': self.np_id.complete_name or '',
            'district_name': self.district_id.name or '',  # self.district_id.complete_name or '', ADD complete_name to model
            'state_name': self.state_id.name or '',  # self.state_id.complete_name or '', ADD complete_name to model
            'zip': self.zip or '',
            'country_name': self.country_id.name or '',
        })
        # for field in self._formatting_address_fields():
        #     args[field] = getattr(self, field) or ''

        list_from_dict = [value for value in args.values() if value !='']
        address_formatted = ", ".join(list_from_dict)
        # address_formatted = address_format.format(**args)
        # address_formatted = address_formatted.split() 
        # address_formatted = ", ".join(address_formatted)
        return address_formatted
        # return address_format % args

    @api.depends(lambda self: self._display_address_depends())
    def _compute_complete_address(self):
        for partner in self:
            partner.complete_address = partner._display_address()

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return self._formatting_address_fields() + [
            'country_id', 'state_id', 'district_id', 'np_id'
        ]
    # @api.model
    # def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     if (not view_id) and (view_type == 'form') and self._context.get('force_email'):
    #         view_id = self.env.ref('dgf_asset_base.view_dgf_asset_onms_form').id
    #     res = super(DgfAsset, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         res['arch'] = self._fields_view_get_address(res['arch'])
    #     return res

class DgfAssetRegisterType(models.Model):
    _description = 'Тип реєстру'
    _name = 'dgf.asset.register.type'
    _order = 'sequence'
    _parent_store = True

    sequence = fields.Integer('Послідовність', default=10)
    name = fields.Char(string='Найменування', required=True)
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
