# -*- coding: utf-8 -*-

from odoo import api, models


class ReportProject(models.AbstractModel):
    _name = 'report.dgf_task_type.dgf_project_tasks_container'
    _description = "Project DGF Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'project.project',
            'docs': self._get_report_data(),
            # слід повертати в _get_report_data() словник
            # { 'project': project(1,)
            #    'docs': task_types}
        }
        return values

    def _get_report_data(self):
        res = {}
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
