# -*- coding: utf-8 -*-

import logging
# import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
# from odoo.osv import expression

# from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class ClassifierKATOTTG(models.Model):
    _name = "stat.classifier.katottg"
    _description = "КАТОТТГ"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'id'

    code1 = fields.Char(string='Перший рівень')


    					

    code2 = fields.Char(string='Другий рівень')
    code3 = fields.Char(string='Третій рівень')
    code4 = fields.Char(string='Четвертий рівень')
    code5 = fields.Char(string='Додатковий рівень')
    category = fields.Char(string="Категорія об’єкта")
    name = fields.Char(string='Назва об’єкта', index=True, required=False)
    level = fields.Integer('Рівень в ієрархії')
    code = fields.Char(string='Код', required=False)
    parent_id = fields.Many2one('stat.classifier.katottg', string='Батьківський елемент', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('stat.classifier.katottg', 'parent_id', string='Дочірні елементи')

    parent_region = fields.Many2one('stat.classifier.katottg', string='Регіон', index=True, ondelete='cascade')
    parent_district = fields.Many2one('stat.classifier.katottg', string='Район', index=True, ondelete='cascade')
    parent_ttg = fields.Many2one('stat.classifier.katottg', string='Територіальна громада', index=True, ondelete='cascade')
    parent_np = fields.Many2one('stat.classifier.katottg', string='Населений пункт', index=True, ondelete='cascade')
    # @api.depends('name', 'parent_id.complete_name')
    # def _compute_complete_name(self):
    #     for category in self:
    #         if category.parent_id:
    #             category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
    #         else:
    #             category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True


# ----
# Methods
# ----

#  TODO: process 'parent_id' with SQL instead 'set_parent()'
    def clear_level(self):
        records = self.search([], order='id')
        _logger.info('Records to update: {0}'.format(len(records)))
        sql_query = "UPDATE stat_classifier_katottg SET level = null, code = null, parent_id = null, parent_region = null, parent_district = null, parent_ttg = null, parent_np = null;"
        self.env.cr.execute(sql_query)
        _logger.info('Done.')

    def set_levels(self):
        for level in range(1, 6):
            if level == 5:
                recordset = self.search([('code{}'.format(level), "!=", False)], order='id')
            else:
                recordset = self.search([('code{}'.format(level), "!=", False), ('code{}'.format(level + 1), "=", False)], order='id')

            _logger.info('Records to update: {0}'.format(len(recordset)))

            for record in recordset:
                query = "UPDATE stat_classifier_katottg SET level = {0}, code = '{1}' where id = {2};".format(level, record['code{}'.format(level)], record.id)
                self._cr.execute(query)
            recordset.flush()
            _logger.info('Level {0} done.'.format(level))
        _logger.info('Action done.')

    def set_parents(self):
        for level in range(1, 4):
            if level == 3:
                result = self.read_group([("level", "=", level + 2)],
                                         fields=['code4'],
                                         groupby=['code4'])
                domain = [d['code4'] for d in result if 'code4' in d]
                recordset = self.search([('code', "in", domain)], order='id')
            else:
                recordset = self.search([('level', "=", level)], order='id')
            query_template = "UPDATE stat_classifier_katottg SET parent_id = {0} where level in ({1}) and code{2} = '{3}';"

            _logger.info('Groups of records to update: {0}'.format(len(recordset)))

            for record in recordset:
                if level == 2:
                    levels = '{0}, {1}'.format(level + 1, level + 2)
                    query = query_template.format(record.id, levels, level, record.code)
                elif level == 3:
                    levels = '{0}'.format(level + 2)
                    query = query_template.format(record.id, levels, level + 1, record.code)
                else:
                    levels = '{0}'.format(level + 1)
                    query = query_template.format(record.id, levels, level, record.code)

                self._cr.execute(query)
            recordset.flush()
            _logger.info('Level {0} done.'.format(level))
        _logger.info('Action done.')

    def set_hierarchy(self):
        for level in range(1, 6):
            if level == 1:
                recordset = self.search([('level', "=", level)], order='id')
                query_template = "UPDATE stat_classifier_katottg SET parent_region = {0} where level not in ({1}) and code{2} = '{3}';"
                levels = '{0}'.format(level)
            elif level == 2:
                recordset = self.search([('level', "=", level)], order='id')
                query_template = "UPDATE stat_classifier_katottg SET parent_district = {0} where level not in ({1}) and code{2} = '{3}';"
                levels = '{0}'.format(level)
            elif level == 3:
                recordset = self.search([('level', "=", level)], order='id')
                query_template = "UPDATE stat_classifier_katottg SET parent_ttg = {0} where level not in ({1}) and code{2} = '{3}';"
                levels = '{0}'.format(level)
            elif level == 4:
                result = self.read_group([("level", "=", level + 1)],
                                         fields=['code4'],
                                         groupby=['code4'])
                domain = [d['code4'] for d in result if 'code4' in d]
                recordset = self.search([('code', "in", domain)], order='id')
                query_template = "UPDATE stat_classifier_katottg SET parent_np = {0} where level in ({1}) and code{2} = '{3}';"
                levels = '{0}'.format(level + 1)
            elif level == 5:
                recordset = self.search([('category', "=", 'K')], order='id')
                query_template = "UPDATE stat_classifier_katottg SET parent_district = {0}, parent_ttg = {0}, parent_np = {0} where code4 = '{1}';"
            # else:
            #     recordset = self.search([('level', "=", level)], order='id')
            #     query_template = "UPDATE stat_classifier_katottg SET parent_ttg = {0} where level not in ({1}) and code{2} = '{3}';"
            #     levels = '{0}'.format(level)

            _logger.info('Groups of records to update: {0}'.format(len(recordset)))

            for record in recordset:
                if level == 5:
                    query = query_template.format(record.id, record.code)
                else:
                    query = query_template.format(record.id, levels, level, record.code)

                self._cr.execute(query)
            recordset.flush()
            _logger.info('Level {0} done.'.format(level))
        _logger.info('Action done.')

    def action_view_district(self):
        return {
            'name': 'Райони',
            'domain': [('parent_region', '=', self.id), ('level', '=', 2)],
            'view_type': 'form',
            'res_model': 'stat.classifier.katottg',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def action_view_ttg(self):
        return {
            'name': 'Територіальні громади',
            'domain': [('parent_region', '=', self.id), ('level', '=', 3)],
            'view_type': 'form',
            'res_model': 'stat.classifier.katottg',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }

    def action_view_cities(self):
        return {
            'name': 'Населені пункти',
            'domain': [('parent_region', '=', self.id), ('level', 'in', (4, 5))],
            'view_type': 'form',
            'res_model': 'stat.classifier.katottg',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window'
        }
