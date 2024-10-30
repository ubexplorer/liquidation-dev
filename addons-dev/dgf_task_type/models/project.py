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
    is_group = fields.Boolean(default=False, string='Група', help="Ознака групи активів.")
    active = fields.Boolean(default=True, string='Активно', help="Чи є запис активним чи архівованим.")
    parent_id = fields.Many2one('dgf.task.type', string='Батьківська категорія', ondelete='cascade')  # index=True,
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
    
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         code = record.code or ''
    #         rec_name = "[{0}] {1}".format(code, record.name)
    #         result.append((record.id, rec_name))
    #     return result

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

    # @api.model
    # def search_panel_select_range(self, field_name, **kwargs):
    # responce = self.env['vkursi.api']._api_freenais(code=self.vat, description=provider_name)


    # for report
    def get_report_data(self):
        # res = {}
        task_types = self.env["dgf.task.type"].search([("is_group", "=", True),])
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
        # res['task_types'] = task_types
        return task_types

    def py3o_lines_layout(self):
        self.ensure_one()
        res = []
        has_sections = False
        subtotal = 0.0
        for line in self.order_line:
            if line.display_type == 'line_section':
                # insert line
                if has_sections:
                    res.append({'subtotal': subtotal})
                subtotal = 0.0  # reset counter
                has_sections = True
            elif not line.display_type:
                subtotal += line.price_subtotal
            res.append({'line': line})
        if has_sections:  # insert last subtotal line
            res.append({'subtotal': subtotal})
        # res:
        # [
        #    {'line': sale_order_line(1) with display_type=='line_section'},
        #    {'line': sale_order_line(2) without display_type},
        #    {'line': sale_order_line(3) without display_type},
        #    {'line': sale_order_line(4) with display_type=='line_note'},
        #    {'subtotal': 8932.23},
        # ]
        return res

    def get_types_action(self):
        res = []
        for record in self:
            task_types = self.get_task_types(record.id)
            for task_type in task_types.get('task_types'):
                # task_name = task_type.name.upper()
                category = {
                    'name': task_type.name, 
                    'id': task_type.id, 
                    'child_ids': task_type.child_ids,
                    'task_ids': task_type.task_ids}
                print(category['name'])
                if task_type.child_ids:
                    for child in task_type.child_ids:
                        category = {
                            'name': child.name,
                            'id': child.id,
                            'child_ids': child.child_ids,
                            'task_ids': child.task_ids}
                        print('  ' + category['name'])
                        for task in child.task_ids:
                            print('    ' + task.name)
                else:
                    for task in task_type.task_ids:
                        print('    ' + task.name)

                # res.append({'category': category})
            # print(res)

    # @api.model
    def get_task_types(self, project_id):
        task_type_ids = self.env["dgf.task.type"].search(
            [
                # ("project_id", "=", project_id),
                ("is_group", "=", True),
            ]
        )
        return {
            "task_types": task_type_ids,
            # "child_ids": child_ids,
            "project_id": project_id,
        }
        # task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', '&', ('stage_id.is_closed', '=', False), ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])

class ProjectTask(models.Model):
    _inherit = 'project.task'

    dgf_type_id = fields.Many2one(
        comodel_name='dgf.task.type', string='Категорія', )
