# pylint:disable=too-many-lines
import logging

from odoo import models, fields, api, tools, _, http, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'project.task'

    code = fields.Char(string='Код', readonly=True, copy=False)


class DgfTask(models.Model):
    # TODO:   _inherit = 'project.task' instead _inherits = {'project.task': 'task_id'}
    _name = "dgf.task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'project.task': 'task_id'}
    _description = 'Заявка щодо активу'
    # _rec_name = 'code'
    # _order = 'request_date DESC'

    task_id = fields.Many2one(
        comodel_name='project.task',
        auto_join=True,
        string='Базове завдання', required=True, readonly=True, ondelete='restrict',
        check_company=True)
    # name = fields.Char(related='task_id.name', inherited=True, readonly=False)
    # code = fields.Char(string='Код', related='task_id.code', inherited=True, readonly=True)  # sequence
    # project_id = fields.Many2one(related='task_id.project_id', inherited=True, readonly=False)
    # document_ids = fields.Many2one('dgf.document', string="Рішення щодо заявки", ondelete='restrict', index=True)
    # internal_note_text = fields.Html(string='Внутрішні примітки')

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


