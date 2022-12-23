# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ['res.company', 'mail.thread', 'mail.activity.mixin']
    # _inherits = {'res.partner': 'partner_id'}
    _name = 'res.company'
    _order = 'dgf_statusdate desc, mfo'

    user_ids = fields.Many2many('res.users', 'res_company_users_dgf_rel', 'cid', 'user_id', string='Accepted Users')

    active = fields.Boolean(
        default=True, help="The active field allows you to hide the category without removing it.")
    fullname = fields.Char(related='partner_id.fullname', store=True, readonly=False)
    # category_id = fields.Many2many(related='partner_id.category_id', store=True, readonly=False)
    mfo = fields.Char(string='МФО')
    ceo_id = fields.Many2one(
        comodel_name='res.partner',
        ondelete='restrict',
        string='Керівник',
        domain=[('active', '=', True), ('is_company', '=', False)])
    dgf_status_id = fields.Many2one(
        'generic.dictionary', string='Статус ліквідації', tracking=True)
    dgf_statusdate = fields.Date(
        index=True, string='Дата статусу', tracking=True)
    dgf_terminationdateplan = fields.Date(
        index=True, string='Ліквідація очікується')
