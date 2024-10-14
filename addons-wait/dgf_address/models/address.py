import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')


class AddressType(models.Model):
    _name = 'dgf.address.type'
    _description = 'Address type'

    name = fields.Char()

    active = fields.Boolean(
        default=True, )


class AddressMixin(models.AbstractModel):
    _name = 'dgf.address.mixin'
    _description = 'Address mixin'

    street = fields.Char()
    # street2 = fields.Char()
    street2 = fields.Many2one(comodel_name='stat.classifier.katottg', ondelete='restrict', domain="[('parent_id', '=', state_id), ('level', '=', 2)]")
    zip = fields.Char(change_default=True, )
    city = fields.Char()
    # state_id = fields.Many2one(comodel_name='res.country.state', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    state_id = fields.Many2one(comodel_name='stat.classifier.katottg', ondelete='restrict', domain="[('level', '=', 1)]")
    country_id = fields.Many2one(comodel_name='res.country', ondelete='restrict')
    latitude = fields.Float(digits=(16, 5))
    longitude = fields.Float(digits=(16, 5))

    @api.model
    def _formatting_address_fields(self):
        return list(ADDRESS_FIELDS)

    def _get_country_name(self):
        self.ensure_one()
        return self.country_id.name or ''

    def _get_state_name(self):
        self.ensure_one()
        return self.state_id.name or ''

    @api.model
    def _get_default_address_format(self):
        # return '%(street)s\n%(street2)s\n%(city)s %(state_code)s ' \
        #        '%(zip)s\n%(country_name)s'
        return "%(street)s %(city)s %(district_name)s %(state_name)s %(zip)s %(country_name)s"
        # return "{street} {np_name} {district_name} {state_name} {zip} {country_name}"

    @api.model
    def _get_address_format(self):
        self.ensure_one()
        return self.country_id.address_format or \
            self._get_default_address_format()

    # def _display_address(self):
    #     self.ensure_one()
    #     args = {
    #         'state_code': self.state_id.code or '',
    #         'state_name': self.state_id.name or '',
    #         'country_code': self.country_id.code or '',
    #         'country_name': self._get_country_name(), }
    #     for field in self._formatting_address_fields():
    #         args[field] = getattr(self, field) or ''
    #     return '%(street)s\n%(street2)s\n%(city)s %(state_code)s ' \
    #            '%(zip)s\n%(country_name)s' % args
    #     # return self._get_address_format() % args

    def _display_address(self):
        self.ensure_one()
        args = {
            'street': self.street or '',
            'city': self.city or '',
            # 'street2': self.street2 or '', # district_name
            'street2': self.street2.name or '', # district_name
            'state_name': self.state_id.name or '',
            'country_name': self._get_country_name(), }
        # for field in self._formatting_address_fields():
        #     args[field] = getattr(self, field) or ''

        list_from_dict = [value for value in args.values() if value !='']
        address_formatted = ", ".join(list_from_dict)
        return address_formatted

        # # TODO:
        # address_format = self._get_address_format()
        # args = {
        #     'street': self.street or '',
        #     'np_name': self.np_id.complete_name or '',
        #     'district_name': self.district_id.name or '',  # self.district_id.complete_name or '', ADD complete_name to model
        #     'state_name': self.state_id.name or '',  # self.state_id.complete_name or '', ADD complete_name to model
        #     'zip': self.zip or '',
        #     'country_name': self.country_id.name or '',
        # }
        # list_from_dict = [value for value in args.values() if value !='']
        # address_formatted = ", ".join(list_from_dict)
        # # address_formatted = address_format.format(**args)
        # return address_formatted
        # # return address_format % args

class Address(models.Model):
    _name = 'dgf.address'
    _description = 'Address'
    _inherit = 'dgf.address.mixin'

    name = fields.Char(compute='_compute_name', store=True, )
    active = fields.Boolean(default=True, )
    type_id = fields.Many2one(comodel_name='dgf.address.type', ondelete='restrict', )

    @api.depends('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def _compute_name(self):
        for obj in self:
            obj.name = obj._display_address()
