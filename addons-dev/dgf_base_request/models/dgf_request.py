# pylint:disable=too-many-lines
import logging

from odoo import models, fields, api, tools, _, http, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DgfBaseRequest(models.Model):
    _name = "dgf.base.request"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'base.stage.abstract',
        # 'base.category.abstract'
    ]
    _description = 'Заявка щодо активу'
    _rec_name = 'code'
    _order = 'request_date DESC'

    name = fields.Char(readonly=False, index=True, copy=False)
    code = fields.Char(string='Код', readonly=True, copy=False)  # sequence
    company_id = fields.Many2one('res.company', string='Банк-заявник', required=True)
    partner_id = fields.Many2one('res.partner', 'Контрагент', index=True, tracking=True, ondelete='restrict')
    request_date = fields.Date('Дата заявки', tracking=False)
    request_number = fields.Char('Номер заявки', tracking=False)
    document_id = fields.Many2one('dgf.document', string="Рішення щодо заявки", ondelete='restrict', index=True)
    close_date = fields.Date('Фактична дата виконання')
    description = fields.Text('Опис')
    category_id = fields.Many2one('dgf.base.request.category', string='Категорія заявки')
    category_code = fields.Char(string='Код типу запиту', related="category_id.code", readonly=True)
    stage_id = fields.Many2one(string='Статус')
    stage_code = fields.Char(string='Код статусу', related="stage_id.code", readonly=True)
    active = fields.Boolean(string='Активно', default=True)
    done = fields.Boolean(string='Виконано', related='stage_id.is_closed')
    user_id = fields.Many2one('res.users', string='Виконавець', default=lambda self: self.env.user, tracking=True)
    # child_request_id = fields.Many2one(string="Похідна заявка")
    # owner_user_id = fields.Many2one('res.users', string='Created by User', default=lambda s: s.env.uid)
    internal_note_text = fields.Html(string='Внутрішні примітки')

    # def action_button_show_subrequests(self):
    #     action = self.get_action_by_xmlid(
    #         'generic_request.action_request_window',
    #         context={'generic_request_parent_id': self.id,
    #                  'search_default_filter_open': True},
    #         domain=[('parent_id', '=', self.id)],
    #     )
    #     action.update({
    #         'name': _('Subrequests'),
    #         'display_name': _('Subrequests'),
    #     })
    #     return action


class DgfBaseRequestCategory(models.Model):
    _description = 'Категорія заявки'
    _name = 'dgf.base.request.category'
    _order = 'sequence'
    _parent_store = True

    sequence = fields.Integer('Послідовність', default=1)
    name = fields.Char(string='Найменування', required=True)
    # full_name = fields.Char(string='Повне найменування', index=True)
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Код', required=False)
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.base.request.category', string='Батьківська категорія', ondelete='cascade')  # index=True,
    parent_path = fields.Char()  # index=True
    child_ids = fields.One2many('dgf.base.request.category', 'parent_id', string='Дочірні категорії')

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
