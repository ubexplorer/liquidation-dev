# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models
# from odoo.exceptions import ValidationError

# from calendar import monthrange
# from dateutil.relativedelta import relativedelta
# from dateutil.rrule import rrule, rruleset, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU


class ProjectTaskRecurrence(models.Model):
    _inherit = "project.task.recurrence"

    @api.model
    def _get_recurring_fields(self):
        # Values in Super Class
        # return ['allowed_user_ids', 'company_id', 'description', 'displayed_image_id', 'email_cc',
        #         'parent_id', 'partner_email', 'partner_id', 'partner_phone', 'planned_hours',
        #         'project_id', 'project_privacy_visibility', 'sequence', 'tag_ids', 'recurrence_id',
        #         'name', 'recurring_task']
        res = super(ProjectTaskRecurrence, self)._get_recurring_fields()
        additional_recurring_fields = ['task_reminder', 'template_id']
        res.extend(additional_recurring_fields)
        return res

    def _new_task_values(self, task):
        res = super(ProjectTaskRecurrence, self)._new_task_values(task)
        if task.template_id is not None:
            res['date_deadline'] = datetime.now().date()
        return res
