import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TaskType(models.Model):
    _name = 'dgf.task.type'
    _description = 'Категорії завдань'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    # _order = 'complete_name'
    _order = 'sequence'

    sequence = fields.Integer('Послідовність', default=10)
    name = fields.Char(string='Найменування', required=True)
    # singular_name = fields.Char('Найменування в однині')
    complete_name = fields.Char('Повне найменування', compute='_compute_complete_name', store=True)
    code = fields.Char(string='Код', required=False)
    project_id = fields.Many2one('project.project', string='Проект', index=True, ondelete='cascade')
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи активів.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.task.type', string='Батьківська категорія', index=True, ondelete='cascade')
    parent_path = fields.Char()  # index=True
    child_ids = fields.One2many('dgf.task.type', 'parent_id', string='Дочірні категорії')
    task_ids = fields.One2many('project.task', 'dgf_type_id', string='Завдання категорії')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
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


class Project(models.Model):
    _inherit = [
        'project.project',
        # 'base'
        ]

    # for report
    def get_report_data(self):
        task_types = self.env["dgf.task.type"].search([("is_group", "=", True), ("project_id", "=", self.id)])
        for task_type in task_types:
            print(task_type.name)
            if task_type.child_ids:
                for child in task_type.child_ids:
                    print('  ' + child.name)
                    for task in child.task_ids:
                        print('    ' + task.name)
            else:
                for task in task_type.task_ids:
                    print('    ' + task.name)
        return task_types


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # project_id = fields.Many2one('project.project', string='Project',
    #     compute='_compute_project_id', store=True, readonly=False,
    #     index=True, tracking=True, check_company=True, change_default=True)
    dgf_type_id = fields.Many2one(
        comodel_name='dgf.task.type',
        string='Категорія',
        domain="[('project_id', '=', project_id)]"
        )
