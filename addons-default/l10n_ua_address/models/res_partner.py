# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, models, fields
from odoo.tools.translate import _


class Partner(models.Model):
    _inherit = 'res.partner'

    # country_enforce_cities = fields.Boolean(related='country_id.enforce_cities', readonly=True)

    country_id = fields.Many2one('res.country', default=lambda self: self._default_country())
    district_id = fields.Many2one('res.country.district', string='Район')
    np_id = fields.Many2one('res.country.np', string='Населений пункт')

    def _default_country(self):
        # country_id = self.env.ref('base.ua').id
        return self.env.ref('base.ua').id

    @api.onchange("state_id")
    def _onchange_state_id(self):
        self.district_id = False
        self.np_id = False

    @api.onchange("district_id")
    def _onchange_district_id(self):
        self.np_id = False

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return super(Partner, self)._address_fields() + ['district_id', 'np_id', ]

    # @api.model
    # def _fields_view_get_address(self, arch):
    #     arch = super(Partner, self)._fields_view_get_address(arch)
    #     # render the partner address accordingly to address_view_id
    #     doc = etree.fromstring(arch)
    #     if doc.xpath("//field[@name='city_id']"):
    #         return arch

    #     replacement_xml = """
    #         <div>
    #             <field name="country_enforce_cities" invisible="1"/>
    #             <field name="parent_id" invisible="1"/>
    #             <field name='city' placeholder="%(placeholder)s" class="o_address_city"
    #                 attrs="{
    #                     'invisible': [('country_enforce_cities', '=', True), '|', ('city_id', '!=', False), ('city', 'in', ['', False ])],
    #                     'readonly': [('type', '=', 'contact')%(parent_condition)s]
    #                 }"
    #             />
    #             <field name='city_id' placeholder="%(placeholder)s" string="%(placeholder)s" class="o_address_city"
    #                 context="{'default_country_id': country_id,
    #                           'default_name': city,
    #                           'default_zipcode': zip,
    #                           'default_state_id': state_id}"
    #                 domain="[('country_id', '=', country_id), ('state_id', '=?', state_id)]"
    #                 attrs="{
    #                     'invisible': [('country_enforce_cities', '=', False)],
    #                     'readonly': [('type', '=', 'contact')%(parent_condition)s]
    #                 }"
    #             />
    #         </div>
    #     """

    #     replacement_data = {
    #         'placeholder': _('City'),
    #     }

    #     def _arch_location(node):
    #         in_subview = False
    #         view_type = False
    #         parent = node.getparent()
    #         while parent is not None and (not view_type or not in_subview):
    #             if parent.tag == 'field':
    #                 in_subview = True
    #             elif parent.tag in ['list', 'tree', 'kanban', 'form']:
    #                 view_type = parent.tag
    #             parent = parent.getparent()
    #         return {
    #             'view_type': view_type,
    #             'in_subview': in_subview,
    #         }

    #     for city_node in doc.xpath("//field[@name='city']"):
    #         location = _arch_location(city_node)
    #         replacement_data['parent_condition'] = ''
    #         if location['view_type'] == 'form' or not location['in_subview']:
    #             replacement_data['parent_condition'] = ", ('parent_id', '!=', False)"

    #         replacement_formatted = replacement_xml % replacement_data
    #         for replace_node in etree.fromstring(replacement_formatted).getchildren():
    #             city_node.addprevious(replace_node)
    #         parent = city_node.getparent()
    #         parent.remove(city_node)

    #     arch = etree.tostring(doc, encoding='unicode')
    #     return arch
