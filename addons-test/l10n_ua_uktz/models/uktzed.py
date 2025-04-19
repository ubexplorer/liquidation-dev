import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class UktzedCode(models.Model):
    _name = 'kw.uktzed.code'
    _description = 'Uktzed code'
    _inherit = ['generic.mixin.parent.names']
    _parent_name = 'parent_id'

    name = fields.Char(string='Code', )
    active = fields.Boolean(
        default=True, )
    parent_id = fields.Many2one(
        comodel_name='kw.uktzed.code', )
    title = fields.Char()
    child_ids = fields.Many2many(
        comodel_name='kw.uktzed.code', relation='kw_uktzed_child_rel',
        compute='_compute_child_ids', )
    description = fields.Text()

    def _compute_child_ids(self):
        for obj in self:
            children = self.search([('parent_id', '=', obj.id)])
            obj.child_ids = ([(4, child.id) for child in children]
                             if children else False)
